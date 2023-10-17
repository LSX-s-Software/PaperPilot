import sys
from abc import ABCMeta
from concurrent import futures
from pathlib import Path

import grpc
import grpc.aio
from django.conf import settings
from django.utils.module_loading import import_string
from grpc_reflection.v1alpha import reflection

from paperpilot_common.grpc.signals.wrapper import SignalWrapper
from paperpilot_common.utils.log import get_logger

logger = get_logger("server.grpc.util")


def get_existed_file_path(path: str) -> Path | None:
    if path is None:
        return None

    path = Path(path)

    # 如果路径是绝对路径并且存在，则返回 Path 对象
    if path.is_absolute() and path.exists():
        return path

    # 获取sys.path中的路径列表
    for search_path in sys.path:
        current_path = Path(search_path) / path
        if current_path.exists():
            return current_path

        # 如果未找到文件或路径不存在，则返回 None
    return None


def create_server(address):
    config = getattr(settings, "GRPC_SERVER", dict())
    servicers_list = config.get("servicers", [])  # callbacks to add servicers to the server
    interceptors = load_interceptors(config.get("interceptors", []))
    max_workers = config.get("max_workers", 10)
    maximum_concurrent_rpcs = config.get("maximum_concurrent_rpcs", None)
    options = config.get("options", [])
    is_async = config.get("async", False)
    server_reflection = config.get("reflection", True)

    key_path = get_existed_file_path(config.get("ssl_key", None))
    cert_path = get_existed_file_path(config.get("ssl_cert", None))

    # create a gRPC server
    if is_async is True:
        server = grpc.aio.server(
            interceptors=interceptors, maximum_concurrent_rpcs=maximum_concurrent_rpcs, options=options
        )
    else:
        server = grpc.server(
            thread_pool=futures.ThreadPoolExecutor(max_workers=max_workers),
            interceptors=interceptors,
            maximum_concurrent_rpcs=maximum_concurrent_rpcs,
            options=options,
        )

    service_names = add_servicers(server, servicers_list)
    if server_reflection:
        reflection.enable_server_reflection(service_names, server)
        logger.info("gRPC server reflection enabled")

    if key_path is None or cert_path is None:
        server.add_insecure_port(address)
        logger.info("gRPC server listening on %s", address)
    else:
        key_path = get_existed_file_path(getattr(settings, "GRPC_SSL_KEY", None))
        cert_path = get_existed_file_path(getattr(settings, "GRPC_SSL_CERT", None))

        logger.info(f"Get ssl key path: {key_path}")
        logger.info(f"Get ssl cert path: {cert_path}")

        with open(key_path, "rb") as f:
            private_key = f.read()
        with open(cert_path, "rb") as f:
            certificate_chain = f.read()

        creds = grpc.ssl_server_credentials(
            [
                (
                    private_key,
                    certificate_chain,
                ),
            ]
        )

        server.add_secure_port(address, creds)
        logger.info("gRPC server with ssl listening on %s", address)

    return server


def add_servicers(server, servicers_list):
    """
    Add servicers to the server
    """
    ps = SignalWrapper(server)
    if len(servicers_list) == 0:
        logger.warning("No servicers configured. Did you add GRPSERVER['servicers'] list to settings?")

    services_names = []

    for path in servicers_list:
        logger.debug("Adding servicers from %s", path)
        callback = import_string(path)
        service_name = callback(ps)

        if not service_name:
            continue

        if isinstance(service_name, str):
            service_name = [service_name]

        services_names.extend(service_name)

    services_names.append(reflection.SERVICE_NAME)

    return services_names


def load_interceptors(strings) -> list:
    # Default interceptors
    result = []
    # User defined interceptors
    for path in strings:
        logger.debug("Initializing interceptor from %s", path)
        result.append(import_string(path)())
    return result


def extract_handlers(server):
    for handler in server._state.generic_handlers:
        for path, it in handler._method_handlers.items():
            unary = it.unary_unary
            if unary is None:
                name = "???"
                params = "???"
                abstract = "DOES NOT EXIST"
            else:
                code = it.unary_unary.__code__
                name = code.co_name
                params = ", ".join(code.co_varnames)
                abstract = ""
                if isinstance(it.__class__, ABCMeta):
                    abstract = "NOT IMPLEMENTED"

            yield "{path}: {name}({params}) {abstract}".format(path=path, name=name, params=params, abstract=abstract)
