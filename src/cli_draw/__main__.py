import argparse

from cli_draw.app import run


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cli-draw",
        description="Terminal drawing canvas with mouse support.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Optional ASCII/ANSI canvas file to open for editing.",
    )
    parser.add_argument(
        "--save",
        dest="save_path",
        help="Path to save ANSI-colored output when pressing 's'.",
    )
    args = parser.parse_args()
    run(source_path=args.input, save_path=args.save_path)
