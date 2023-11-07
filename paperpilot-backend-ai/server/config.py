import tomllib
from pathlib import Path

from paperpilot_common.utils.log import get_logger

ROOT = Path(__file__).parent.parent
CONFIG = ROOT / "config.toml"

if not CONFIG.exists():
    get_logger("config").error(f"config file {CONFIG} not found")

with open(CONFIG, "rb") as f:
    data = tomllib.load(f)

if __name__ == "__main__":
    print(data)
