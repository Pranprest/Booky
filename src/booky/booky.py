#!/usr/bin/env python3
"""
    Booky - A command line utility for bookmarking files

    ===
        Author: Pranprest
    ===
"""
from argparse import Namespace, ArgumentParser
from mmap import mmap, ACCESS_READ
from shutil import copyfileobj
from typing import Final
from pathlib import Path
import json
import sys


def _arg_parser() -> ArgumentParser:
    _parser = ArgumentParser(
        description='Bookmark files and use them in other programs.', prog="Booky")

    # Manage bookmarks themselves
    _parser.add_argument('file',
                         type=str,
                         nargs="?",
                         metavar="File/Alias",
                         help="The file/alias that will be used")

    _parser.add_argument('-e', '--env',
                         type=str,
                         default="default",
                         help="Environment that will be used for the bookmarks")

    mutually_exclusive = _parser.add_mutually_exclusive_group()

    # - Also works for modifying existing aliases!
    mutually_exclusive.add_argument('-a', '--add',
                                    '--alias',
                                    type=str,
                                    metavar="ALIAS",
                                    help="Alias that the file will be assigned to.")

    mutually_exclusive.add_argument('-r', '--remove',
                                    action="store_true",
                                    help="Remove a bookmarked file under current ARGS.environment")

    # Do things with the bookmarked files
    mutually_exclusive.add_argument('-o', '--output',
                                    action="store_true",
                                    help="Show file/dir output (cat file or list dir)")

    mutually_exclusive.add_argument('-p', '--path',
                                    action='store_true',
                                    help="Show current file/alias'es path")

    mutually_exclusive.add_argument('-l',
                                    '--list',
                                    '--list-ARGS.env',
                                    action="store_true",
                                    help="Lists every alias in current ARGS.environment")
    return _parser


def echo_file(filepath: Path) -> None:
    with open(filepath, 'rb') as f:
        with mmap(f.fileno(), 0, access=ACCESS_READ) as s:
            copyfileobj(s, sys.stdout.buffer)


def main() -> None:
    # Parse the args!
    ARGS: Final[Namespace] = _arg_parser().parse_args()

    # Create json data file if does'nt exist (or is empty) and reference it in data file
    main_data_file: Final[Path] = Path(f"{Path(__file__).parent.resolve()}/data.json")
    if not main_data_file.exists():
        try:
            with open(main_data_file, 'w') as f:
                f.write("{}")
        except OSError:
            sys.exit(f"Error trying to write default data to {main_data_file}.")

    try:
        with open(main_data_file, "r+") as f:
            app_data: dict = json.load(f)
    except OSError:
        sys.exit(f"Error trying to read {main_data_file}.")

    if ARGS.env is not None and ARGS.env not in app_data:
        # Then create a new one!
        app_data[ARGS.env] = {}
        f.seek(0)
        json.dump(app_data, f, indent=4)
        f.truncate()

    if ARGS.file is not None:
        # If ARGS.file is an alias, set it to the alias'es file
        if ARGS.file in app_data[ARGS.env]:
            ARGS.file = Path(app_data[ARGS.env][ARGS.file]).resolve()
        else:
            ARGS.file = Path(ARGS.file).resolve()

    if ARGS.list:
        # Print alias' folder, if not, print all of current env's variables
        if ARGS.file is not None and ARGS.file.is_dir():
            for path in list(ARGS.file.iterdir()):
                print(path.resolve())
            sys.exit(0)
        print(f"These are the aliases within environment '{ARGS.env}':")
        for key, val in app_data[ARGS.env].items():
            print(f'"{key}": "{val}"')
        sys.exit(0)

    if ARGS.output and ARGS.file is not None:
        if not ARGS.file.exists():
            sys.exit("Not a valid file or directory")

        if ARGS.file.is_file():
            echo_file(ARGS.file)
        else:
            for path in list(ARGS.file.iterdir()):
                print(path.resolve())
        sys.exit(0)

    if ARGS.alias is not None and ARGS.file is not None:
        if not ARGS.file.exists():
            sys.exit(f"Not {ARGS.file} is not a valid file, exiting.")

        # (not necessary), just for readability: alias = ARGS.alias
        app_data[ARGS.env][ARGS.alias] = str(ARGS.file)
        with open(main_data_file, "w") as f:
            f.seek(0)
            json.dump(app_data, f, indent=4)
            f.truncate()

        if ARGS.alias in app_data[ARGS.env]:
            print(f"Alias '{ARGS.alias}' in environment '{ARGS.env}' updated successfully!")
        else:
            print(f"Alias '{ARGS.alias}' added to environment '{ARGS.env}' successfully!")
        sys.exit(0)

    if ARGS.remove and ARGS.file is not None:
        if ARGS.file not in app_data[ARGS.env]:
            sys.exit(f'Alias {ARGS.file} not found under environment {ARGS.env}')
        del app_data[ARGS.env][ARGS.file]
        f.seek(0)
        json.dump(app_data, f, indent=4)
        f.truncate()
        print(f'Alias {ARGS.file} sucessfully removed from environment {ARGS.env}!')
        sys.exit(0)

    if ARGS.file is not None:
        print(ARGS.file)
        sys.exit(0)


if __name__ == '__main__':
    main()
