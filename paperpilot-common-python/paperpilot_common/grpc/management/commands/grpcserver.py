import asyncio
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload

from paperpilot_common.grpc.utils import create_server, extract_handlers
from paperpilot_common.utils.log import get_logger

logger = get_logger("grpcserver")


class Command(BaseCommand):
    help = "Run gRPC server"
    config = getattr(settings, "GRPC_SERVER", dict())
    reload = True

    def add_arguments(self, parser):
        parser.add_argument("--max_workers", type=int, help="Number of workers")
        parser.add_argument("--port", type=int, default=8001, help="Port number to listen")
        parser.add_argument("--noreload", action="store_true", default=False)
        parser.add_argument(
            "--list-handlers", action="store_true", default=False, help="Print all registered endpoints"
        )

    def handle(self, *args, **options):
        is_async = self.config.get("async", False)
        self.reload = not options["noreload"]

        if is_async is True:
            if self.reload:
                logger.warning("ATTENTION! Autoreload is enabled!")
                if hasattr(autoreload, "run_with_reloader"):
                    # Django 2.2. and above
                    autoreload.run_with_reloader(self._serve_async, **options)
                else:
                    # Before Django 2.2.
                    autoreload.main(self._serve_async, None, options)
            else:
                self._serve_async(**options)
        else:
            if self.reload:
                logger.warning("ATTENTION! Autoreload is enabled!")
                if hasattr(autoreload, "run_with_reloader"):
                    # Django 2.2. and above
                    autoreload.run_with_reloader(self._serve, **options)
                else:
                    # Before Django 2.2.
                    autoreload.main(self._serve, None, options)
            else:
                self._serve(**options)

    def _serve(self, max_workers, port, *args, **kwargs):
        autoreload.raise_last_exception()
        logger.info("gRPC server starting at %s" % datetime.datetime.now())

        server = create_server(max_workers, port)
        server.start()

        logger.info("gRPC server is listening port %s" % port)

        if kwargs["list_handlers"] is True:
            logger.info("Registered handlers:")
            for handler in extract_handlers(server):
                logger.info("* %s" % handler)

        server.wait_for_termination()

    def _serve_async(self, max_workers, port, *args, **kwargs):
        autoreload.raise_last_exception()

        async def _main_routine():
            logger.info("gRPC async server starting  at %s" % datetime.datetime.now())

            server = create_server(max_workers, port)

            await server.start()
            logger.info("gRPC async server is listening port %s" % port)

            if kwargs["list_handlers"] is True:
                logger.info("Registered handlers:")
                for handler in extract_handlers(server):
                    logger.info("* %s" % handler)

            await server.wait_for_termination()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        main_task = asyncio.ensure_future(_main_routine())
        loop.run_until_complete(main_task)
