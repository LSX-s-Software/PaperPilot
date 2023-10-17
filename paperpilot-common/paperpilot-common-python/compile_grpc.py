import concurrent.futures
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import grpc_tools
from loguru import logger as default_logger

ROOT = Path(__file__).parent.parent

source_path = ROOT / "paperpilot_common" / "protobuf"
target_path = ROOT / "paperpilot-common-python" / "paperpilot_common" / "protobuf"

# 设置生成protobuf代码文件的文件名
service_list = os.listdir(source_path)

pool = concurrent.futures.ThreadPoolExecutor()

_logger = default_logger.bind(title="compile")
_logger.remove()
fmt = (
    "<green>{time:HH:mm:ss}</green> <red>|</red> "
    "<level>{level.icon}</level> <red>|</red> "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> <red>|</red> "
    "<cyan>[{extra[title]}]</cyan> <red>-</red> <level>{message}</level>"
)
_logger.add(sys.stdout, format=fmt, level="DEBUG")


def get_logger(title: str | None = None):
    """
    Get logger
    :param title: title of logger (default: None)
    :return: logger
    """
    return _logger.bind(title=title) if title else _logger


class Task:
    title: str
    command: str | list[str]

    check: bool = (True,)
    quiet: bool = (False,)
    timeout: int | None = None

    process: subprocess.Popen | None = None
    future: concurrent.futures.Future | None = None
    logger: default_logger

    running: bool = False

    def __init__(
        self,
        command: str | list[str],
        title: str | None = None,
    ):
        """
        Task
        :param command: to run
        :param title: title of command (default: 'task')
        """
        self.title = title if title else "task"
        self.command = command
        self.logger = get_logger(self.title)

    def run(
        self,
        wait: bool = True,
        check: bool = True,
        quiet: bool = False,
    ) -> subprocess.Popen | concurrent.futures.Future:
        """
        Run task
        :param wait: wait for task to finish (default: True)
        :param check: check return code, throw exception when task finished (default: True)
        :param quiet: quiet output (default: False)
        :return: subprocess.Popen (wait) or concurrent.futures.Future (not wait)
        """
        self.process = None
        self.running = True
        self.check = check
        self.quiet = quiet

        self.future = pool.submit(self._run)

        if wait:
            return self.wait()

        return self.future

    def _run(self) -> subprocess.Popen:
        """
        Run task synchronously
        """
        output = []
        self.process = subprocess.Popen(
            self.command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        # display and record task output
        def _output():
            for line in self.process.stdout:
                if not self.running:
                    return
                output.append(line.strip())
                if not self.quiet:
                    self.logger.debug(line.strip())

        output_thread = threading.Thread(target=_output)
        output_thread.start()

        output_thread.join()
        self.process.wait()
        # replace stdout(stream) with output(str)
        self.process.stdout = output

        return self.process

    def wait(self) -> subprocess.Popen:
        """
        Wait for task to finish
        :return: subprocess.Popen
        """
        self.process = self.future.result()
        self.running = False

        if self.check and self.process.returncode != 0:
            self.logger.error("Return code: {}", self.process.returncode)
            raise subprocess.CalledProcessError(self.process.returncode, self.command)

        return self.process

    @property
    def returncode(self):
        return self.process.returncode

    @property
    def exited(self):
        if self.process is None:
            return False
        return self.process.poll() is not None


def compile_service(service: str):
    service_root = target_path / service
    logger = get_logger(service)

    logger.info("Start compile service")

    for file_path in source_path.glob(f"{service}/*.proto"):
        command = [
            "python",
            "-m",
            "grpc_tools.protoc",
            f"--mypy_grpc_out={target_path.parent.parent}",
            f"--mypy_out={target_path.parent.parent}",
            f"--python_out={target_path.parent.parent}",
            f"--grpc_python_out={target_path.parent.parent}",
            f"--proto_path={source_path.parent.parent}",
            f'--proto_path={Path(grpc_tools.__file__).parent / "_proto"}',
            f"{file_path}",
        ]

        logger.debug(f"command: {' '.join(command)}")
        task = Task(command, title=f"{service}/{file_path.name}")
        task.run()

    with open(service_root / "__init__.py", "w", encoding="utf-8") as f:
        f.writelines("")

    logger.success("Finish compile service")


def prepare():
    shutil.rmtree(target_path, ignore_errors=True)
    os.makedirs(target_path, exist_ok=True)

    if not os.path.exists(target_path / "__init__.py"):
        with open(target_path / "__init__.py", "w", encoding="utf-8") as f:
            f.writelines("")


if __name__ == "__main__":
    prepare()

    for service_name in service_list:
        compile_service(service_name)
