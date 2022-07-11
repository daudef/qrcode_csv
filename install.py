from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
import os
import sys

if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10 or later is required")


APP_NAME = "qrcode_csv"


DEFAULT_INSTALL_DIR = Path.home() / ".local" / "bin"
APP_DIR = Path(__file__).parent


@dataclass(frozen=True, kw_only=True)
class Options:
    install_dir_path: Path

    @classmethod
    def from_argv(cls):
        parser = ArgumentParser(description=f"Install {APP_NAME}")
        parser.add_argument(
            "--install-dir-path",
            type=Path,
            default=DEFAULT_INSTALL_DIR,
            help=f"Path to a directory to install {APP_NAME}",
            dest="install_dir_path",
        )
        return cls(**vars(parser.parse_args()))


def add_local_bin_path():
    local_bin_dir = Path("~/.local/bin").expanduser().resolve()
    for str_path in os.environ["PATH"].split(":"):
        if Path(str_path) == local_bin_dir:
            return
    print("Adding ~/.local/bin to PATH")
    for f in [Path("~/.bashrc"), Path("~/.zshrc")]:
        if f.exists():
            with f.open(mode="a", encoding="utf-8") as fp:
                fp.write(f'\nPATH="$PATH:{local_bin_dir}"\n')
            return
    raise RuntimeError("Could not find ~/.bashrc or ~/.zshrc")


def main():
    options = Options.from_argv()
    os.chdir(APP_DIR)
    add_local_bin_path()
    if "env" not in set(p.name for p in APP_DIR.iterdir()):
        os.system("python3 -m venv env && source env/bin/activate")
        os.system("env/bin/pip install -r requirements.txt")
    executable_path = options.install_dir_path / f"{APP_NAME}"
    if executable_path.exists():
        print(f"{executable_path} already exists")
        return
    executable_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Installing {APP_NAME} to {executable_path}")
    with executable_path.open(mode="w", encoding="utf-8") as f:
        f.write(
            f"""#!/usr/bin/env sh
source {APP_DIR}/env/bin/activate
python3 {APP_DIR}/{APP_NAME}.py $@"""
        )
    os.chmod(executable_path, 0o755)


if __name__ == "__main__":
    main()
