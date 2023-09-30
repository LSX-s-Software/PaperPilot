import abc
import uuid
from asyncio import iscoroutine
from typing import Any, Callable, Optional, Tuple

import grpc
from grpc import aio as grpc_aio  # Needed for grpcio pre-1.33.2

from paperpilot_common.helper.context import WithContext, context_proxy


class BaseMiddleware(grpc.ServerInterceptor, metaclass=abc.ABCMeta):
    """Base class for server-side interceptors.

    To implement an interceptor, subclass this class and override the intercept method.
    """

    @property
    def method(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.method

    @property
    def package(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.package

    @property
    def method_name(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.method_name

    @property
    def service(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.service

    @property
    def metadata_dict(self) -> dict:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.metadata_dict

    @staticmethod
    def _context_handle(handler_call_details: grpc.HandlerCallDetails) -> None:
        method: str = handler_call_details.method  # type: ignore
        _, package_and_service, method_name = method.split("/")
        *maybe_package, service = package_and_service.rsplit(".", maxsplit=1)
        package = maybe_package[0] if maybe_package else ""

        metadata_dict = {}
        for item in handler_call_details.invocation_metadata:  # type:ignore
            metadata_dict.update({item.key: item.value})

        context_proxy.req_id = metadata_dict.get("request_id", str(uuid.uuid4()))
        context_proxy.method = method
        context_proxy.package = package
        context_proxy.service = service
        context_proxy.method_name = method_name
        context_proxy.metadata_dict = metadata_dict
        context_proxy.inited = True

    @abc.abstractmethod
    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.ServicerContext,
        method_name: str,
    ) -> Any:  # pragma: no cover
        """Override this method to implement a custom interceptor.

        You should call method(request_or_iterator, context) to invoke the next handler
        (either the RPC method implementation, or the next interceptor in the list).

        Args:
            method: Either the RPC method implementation, or the next interceptor in
                the chain.
            request_or_iterator: The RPC request, as a protobuf message if it is a
                unary request, or an iterator of protobuf messages if it is a streaming
                request.
            context: The ServicerContext pass by gRPC to the service.
            method_name: A string of the form "/protobuf.package.Service/Method"

        Returns:
            This should return the result of method(request, context), which
            is typically the RPC method response, as a protobuf message, or an
            iterator of protobuf messages for streaming responses. The interceptor is
            free to modify this in some way, however.
        """
        return method(request_or_iterator, context)

    # Implementation of grpc.ServerInterceptor, do not override.
    def intercept_service(
        self,
        continuation: Callable[[grpc.HandlerCallDetails], Optional[grpc.RpcMethodHandler]],
        handler_call_details: grpc.HandlerCallDetails,
    ) -> Optional[grpc.RpcMethodHandler]:
        """Implementation of grpc.ServerInterceptor.

        This is not part of the grpc_interceptor.ServerInterceptor API, but must have
        a public name. Do not override it, unless you know what you're doing.
        """
        next_handler: Optional[grpc.RpcMethodHandler] = continuation(handler_call_details)
        # Returns None if the method isn't implemented.
        if next_handler is None:
            return None
        handler_factory, next_handler_method, grpc_type = _get_factory_and_method(next_handler)

        def invoke_intercept_method(request_or_iterator: Any, context: grpc.ServicerContext) -> Any:
            method_name = handler_call_details.method
            if not context_proxy.inited:
                with WithContext():
                    self._context_handle(handler_call_details)
                    context_proxy.grpc_type = grpc_type

            return self.intercept(next_handler_method, request_or_iterator, context, method_name)

        return handler_factory(
            invoke_intercept_method,
            request_deserializer=next_handler.request_deserializer,  # type: ignore
            response_serializer=next_handler.response_serializer,  # type: ignore
        )


class AsyncServerMiddleware(grpc_aio.ServerInterceptor, metaclass=abc.ABCMeta):
    """Base class for asyncio server-side interceptors.

    To implement an interceptor, subclass this class and override the intercept method.
    """

    @property
    def method(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.method

    @property
    def package(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.package

    @property
    def method_name(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.method_name

    @property
    def service(self) -> str:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.service

    @property
    def metadata_dict(self) -> dict:
        if not context_proxy.inited:
            raise ValueError("Not init")
        return context_proxy.metadata_dict

    @staticmethod
    def _context_handle(handler_call_details: grpc.HandlerCallDetails) -> None:
        method: str = handler_call_details.method  # type: ignore
        _, package_and_service, method_name = method.split("/")
        *maybe_package, service = package_and_service.rsplit(".", maxsplit=1)
        package = maybe_package[0] if maybe_package else ""

        metadata_dict = {}
        for item in handler_call_details.invocation_metadata:  # type:ignore
            metadata_dict.update({item.key: item.value})

        context_proxy.req_id = metadata_dict.get("request_id", str(uuid.uuid4()))
        context_proxy.method = method
        context_proxy.package = package
        context_proxy.service = service
        context_proxy.method_name = method_name
        context_proxy.metadata_dict = metadata_dict
        context_proxy.inited = True

    @abc.abstractmethod
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc_aio.ServicerContext,
        method_name: str,
    ) -> Any:  # pragma: no cover
        """Override this method to implement a custom interceptor.

        You should await method(request_or_iterator, context) to invoke the next handler
        (either the RPC method implementation, or the next interceptor in the list).

        Args:
            method: Either the RPC method implementation, or the next interceptor in
                the chain.
            request_or_iterator: The RPC request, as a protobuf message if it is a
                unary request, or an iterator of protobuf messages if it is a streaming
                request.
            context: The ServicerContext pass by gRPC to the service.
            method_name: A string of the form "/protobuf.package.Service/Method"

        Returns:
            This should return the result of method(request_or_iterator, context),
            which is typically the RPC method response, as a protobuf message. The
            interceptor is free to modify this in some way, however.
        """
        response_or_iterator = method(request_or_iterator, context)
        if hasattr(response_or_iterator, "__aiter__"):
            return response_or_iterator
        else:
            return await response_or_iterator

    # Implementation of grpc.ServerInterceptor, do not override.
    async def intercept_service(self, continuation, handler_call_details):
        """Implementation of grpc.aio.ServerInterceptor.

        This is not part of the grpc_interceptor.AsyncServerInterceptor API, but must
        have a public name. Do not override it, unless you know what you're doing.
        """
        next_handler = await continuation(handler_call_details)
        handler_factory, next_handler_method, grpc_type = _get_factory_and_method(next_handler)

        if next_handler.response_streaming:

            async def invoke_intercept_method(request, context):
                method_name = handler_call_details.method
                if not context_proxy.inited:
                    with WithContext():
                        self._context_handle(handler_call_details)
                        context_proxy.grpc_type = grpc_type
                coroutine_or_asyncgen = self.intercept(
                    next_handler_method,
                    request,
                    context,
                    method_name,
                )

                # Async server streaming handlers return async_generator, because they
                # use the async def + yield syntax. However, this is NOT a coroutine
                # and hence is not awaitable. This can be a problem if the interceptor
                # ignores the individual streaming response items and simply returns the
                # result of method(request, context). In that case the interceptor IS a
                # coroutine, and hence should be awaited. In both cases, we need
                # something we can iterate over so that THIS function is an
                # async_generator like the actual RPC method.
                if iscoroutine(coroutine_or_asyncgen):
                    asyncgen_or_none = await coroutine_or_asyncgen
                    # If a handler is using the read/write API, it will return None.
                    if not asyncgen_or_none:
                        return
                    asyncgen = asyncgen_or_none
                else:
                    asyncgen = coroutine_or_asyncgen

                async for r in asyncgen:
                    yield r

        else:

            async def invoke_intercept_method(request, context):
                method_name = handler_call_details.method
                if not context_proxy.inited:
                    with WithContext():
                        self._context_handle(handler_call_details)
                        context_proxy.grpc_type = grpc_type
                return await self.intercept(
                    next_handler_method,
                    request,
                    context,
                    method_name,
                )

        return handler_factory(
            invoke_intercept_method,
            request_deserializer=next_handler.request_deserializer,
            response_serializer=next_handler.response_serializer,
        )


def _get_factory_and_method(
    rpc_handler: grpc.RpcMethodHandler,
) -> Tuple[Callable, Callable, str]:
    if rpc_handler.unary_unary:  # type: ignore
        return grpc.unary_unary_rpc_method_handler, rpc_handler.unary_unary, "unary_unary"  # type: ignore
    elif rpc_handler.unary_stream:  # type: ignore
        return grpc.unary_stream_rpc_method_handler, rpc_handler.unary_stream, "unary_stream"  # type: ignore
    elif rpc_handler.stream_unary:  # type: ignore
        return grpc.stream_unary_rpc_method_handler, rpc_handler.stream_unary, "stream_unary"  # type: ignore
    elif rpc_handler.stream_stream:  # type: ignore
        return grpc.stream_stream_rpc_method_handler, rpc_handler.stream_stream, "stream_stream"  # type: ignore
    else:  # pragma: no cover
        raise RuntimeError("RPC handler implementation does not exist")
