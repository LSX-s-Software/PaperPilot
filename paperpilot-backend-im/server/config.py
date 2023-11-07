__data = None


def __getattr__(name):
    global __data

    if not __data:
        import tomllib
        from pathlib import Path

        from paperpilot_common.utils.log import get_logger

        config_file = Path(__file__).parent.parent / "config.toml"

        if not config_file.exists():
            get_logger("config").error(f"config file {config_file} not found")

        with open(config_file, "rb") as f:
            __data = tomllib.load(f)

    return __data[name]
