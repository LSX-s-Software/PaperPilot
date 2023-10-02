#! /usr/bin/env python3
import os
import sys

import pytest


def split_class_and_function(string):
    class_string, function_string = string.split(".", 1)
    return "%s and %s" % (class_string, function_string)


def is_function(string):
    # `True` if it looks like a test function is included in the string.
    return string.startswith("test_") or ".test_" in string


def is_class(string):
    # `True` if first character is uppercase - assume it's a class name.
    return string[0] == string[0].upper()


class PytestTestRunner:
    """Runs pytest to discover and run tests."""

    def __init__(self, verbosity=1, failfast=False, keepdb=False, **kwargs):
        self.verbosity = verbosity
        self.failfast = failfast
        self.keepdb = keepdb

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument(
            "--keepdb",
            action="store_true",
            help="Preserves the test DB between runs.",
        )

    def run_tests(self, test_labels):
        """Run pytest and return the exitcode.

        It translates some of Django's test command option to pytest's.
        """
        import pytest

        argv = []
        if self.verbosity == 0:
            argv.append("--quiet")
        if self.verbosity == 2:
            argv.append("--verbose")
        if self.verbosity == 3:
            argv.append("-vv")
        if self.failfast:
            argv.append("--exitfirst")
        if self.keepdb:
            argv.append("--reuse-db")

        argv.extend(test_labels)
        return pytest.main(argv)


if __name__ == "__main__":
    os.environ["DJANGO_ENV"] = "test"
    os.environ["DJANGO_SECRET_KEY"] = "secret"
    os.environ["DJANGO_SETTINGS_MODULE"] = "server.settings"

    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["CACHE_URL"] = "locmem://"
    os.environ["CELERY_BROKER_URL"] = "memory://"

    if len(sys.argv) > 1:
        pytest_args = sys.argv[1:]
        first_arg = pytest_args[0]

        if "--local" in pytest_args:
            pytest_args.remove("--local")
            pytest_args = [
                "--cov",
                "server",
                "--cov-report",
                "xml",
                "--cov-report",
                "term",
                "--cov-report",
                "html:htmlcov",
            ] + pytest_args
        elif "--coverage" in pytest_args:
            pytest_args.remove("--coverage")
            pytest_args = [
                "--cov",
                "server",
                "--cov-report",
                "xml",
            ] + pytest_args

        if first_arg.startswith("-"):
            # `runtests.py [flags]`
            pytest_args = ["tests"] + pytest_args
        elif is_class(first_arg) and is_function(first_arg):
            # `runtests.py TestCase.test_function [flags]`
            expression = split_class_and_function(first_arg)
            pytest_args = ["tests", "-k", expression] + pytest_args[1:]
        elif is_class(first_arg) or is_function(first_arg):
            # `runtests.py TestCase [flags]`
            # `runtests.py test_function [flags]`
            pytest_args = ["tests", "-k", pytest_args[0]] + pytest_args[1:]
    else:
        pytest_args = []

    sys.exit(pytest.main(pytest_args))
