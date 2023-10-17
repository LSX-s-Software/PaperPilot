import asyncio
import errno
import os
import re
import socketserver
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import grpc.aio._server
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import autoreload
from django.utils.regex_helper import _lazy_re_compile

from paperpilot_common.grpc.utils import create_server
from paperpilot_common.utils.log import get_logger

logger = get_logger("server.grpc")


naiveip_re = _lazy_re_compile(
    r"""^(?:
(?P<addr>
    (?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |         # IPv4 address
    (?P<ipv6>\[[a-fA-F0-9:]+\]) |               # IPv6 address
    (?P<fqdn>[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*) # FQDN
):)?(?P<port>\d+)$""",
    re.X,
)


class Command(BaseCommand):
    help = "Starts a gRPC server."

    # Validation is called explicitly each time the server is reloaded.
    requires_system_checks = []
    stealth_options = ("shutdown_message",)
    suppressed_base_arguments = {"--verbosity", "--traceback"}

    default_addr = "127.0.0.1"
    default_port = "8001"
    protocol = "grpc"

    use_ssl = False

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.creds = None

    def add_arguments(self, parser):
        parser.add_argument("addrport", nargs="?", help="Optional port number, or ipaddr:port")
        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Tells Paperpilot to NOT use the auto-reloader.",
        )
        parser.add_argument(
            "--skip-checks",
            action="store_true",
            help="Skip system checks.",
        )

    def execute(self, *args, **options):
        if options["no_color"]:
            # We rely on the environment because it's currently the only
            # way to reach WSGIRequestHandler. This seems an acceptable
            # compromise considering `runserver` runs indefinitely.
            os.environ["DJANGO_COLORS"] = "nocolor"
        super().execute(*args, **options)

    def handle(self, *args, **options):
        if not options["addrport"]:
            self.addr = ""
            self.port = self.default_port
        else:
            m = re.match(naiveip_re, options["addrport"])
            if m is None:
                raise CommandError('"%s" is not a valid port number ' "or address:port pair." % options["addrport"])
            self.addr, _ipv4, _ipv6, _fqdn, self.port = m.groups()
            if not self.port.isdigit():
                raise CommandError("%r is not a valid port number." % self.port)
        if not self.addr:
            self.addr = self.default_addr
        self.run(**options)

    def run(self, **options):
        """Run the server, using the autoreloader if needed."""
        use_reloader = options["use_reloader"]

        if use_reloader:
            autoreload.run_with_reloader(self.inner_run, **options)
        else:
            self.inner_run(None, **options)

    def inner_run(self, *args, **options):
        # If an exception was silenced in ManagementUtility.execute in order
        # to be raised in the child process, raise it now.
        autoreload.raise_last_exception()

        # 'shutdown_message' is a stealth option.
        shutdown_message = options.get("shutdown_message", "")

        if not options["skip_checks"]:
            self.stdout.write("Performing system checks...\n\n")
            self.check(display_num_errors=True)
        # Need to check migrations here, so can't use the
        # requires_migrations_check attribute.
        self.check_migrations()

        try:
            run(
                self.addr,
                int(self.port),
                on_bind=self.on_bind,
            )
        except OSError as e:
            # Use helpful error messages instead of ugly tracebacks.
            ERRORS = {
                errno.EACCES: "You don't have permission to access that port.",
                errno.EADDRINUSE: "That port is already in use.",
                errno.EADDRNOTAVAIL: "That IP address can't be assigned to.",
            }
            try:
                error_text = ERRORS[e.errno]
            except KeyError:
                error_text = e
            self.stderr.write("Error: %s" % error_text)
            # Need to use an OS exit because sys.exit doesn't work in a thread
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)

    def on_bind(self, server_port):
        quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C"

        if self.addr == "0":
            addr = "0.0.0.0"
        else:
            addr = self.addr

        now = datetime.now().strftime("%B %d, %Y - %X")
        version = self.get_version()
        print(
            f"{now}\n"
            f"Paperpilot version {version}, using settings {settings.SETTINGS_MODULE!r}\n"
            f"Starting development server at {self.protocol}://{addr}:{server_port}/\n"
            f"Quit the server with {quit_command}.",
            file=self.stdout,
        )


async def run_async(
    addr: str,
    port: int,
    on_bind=None,
):
    address = f"{addr}:{port}"

    server = create_server(address)

    if on_bind is not None:
        on_bind(getattr(server, "server_port", port))

    await server.start()
    await server.wait_for_termination()


def run(
    addr,
    port,
    on_bind=None,
):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    main_task = asyncio.ensure_future(run_async(addr, port, on_bind))
    try:
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        logger.info("exit...")
    finally:
        loop.close()
