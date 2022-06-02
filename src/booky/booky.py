#!/usr/bin/env python3
"""
    Booky - A command line utility for bookmarking files

    ===
        Author: Pranprest
    ===
"""
from argparse import Namespace, ArgumentParser
from typing import Final
from pathlib import Path
import json
import sys
import os


def argParser() -> ArgumentParser:
    _parser = ArgumentParser(
        description='Bookmark files and use them in other programs.', prog="Booky")

    # Manage bookmarks themselves
    _parser.add_argument('file',
                         type=str,
                         nARGS="?",
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
                                    help="Bookmarks new file or updates existing one")

    mutually_exclusive.add_argument('-r', '--remove',
                                    action="store_true",
                                    help="Remove a bookmarked file under current environment")

    # Do things with the bookmarked files
    mutually_exclusive.add_argument('-o', '--output',
                                    action="store_true",
                                    help="Show file/dir output (cat file or list dir)")

    mutually_exclusive.add_argument('-p', '--path',
                                    action='store_true',
                                    help="Show current file/alias'es path")

    mutually_exclusive.add_argument('-l',
                                    '--list',
                                    '--list-env',
                                    action="store_true",
                                    help="Lists every alias in current environment")
    return _parser


def echoFile(FilePath: Path) -> None:
    from mmap import mmap, ACCESS_READ
    from shutil import copyfileobj
    with open(FilePath, 'rb') as f:
        with mmap(f.fileno(), 0, access=ACCESS_READ) as s:
            copyfileobj(s, sys.stdout.buffer)


def main() -> None:
    # Create json data file if does'nt exist (or is empty) and reference it in data file
    main_data_file: Final[Path] = Path(f"{Path(__file__).parent.absolute()}/data.json")
    if not main_data_file.exists():
        with open(main_data_file, 'w') as f:
            f.write("{}")

    # Parse the args!
    ARGS: Final[Namespace] = argParser().parse_args()
    env: str = ARGS.env

    # Check if env is actually in there, if not, create new one.
    if ARGS.env is not None:
        with open(main_data_file, "r+") as f:
            full_data: dict = json.load(f)
            if env not in full_data:
                full_data[env] = {}
                f.seek(0)
                json.dump(full_data, f, indent=4)
                f.truncate()

    # If ARGS.file is an alias, set it to the alias'es filepath
    # And make a variable called filepath
    original_alias = ARGS.file
    if ARGS.file is not None:
        # Share this single "read" call for other every argument
        with open(main_data_file, "r") as f:
            full_data = json.load(f)
        if ARGS.file in full_data[env]:
            ARGS.file = Path(full_data[env][ARGS.file])
        else:
            ARGS.file = Path(ARGS.file)
        # If it somehow isn't an absolute path, make it absolute anyways
        filepath = ARGS.file.absolute()

    # Mutulally exclusive arguments:
    # Print alias'es folder, if not, print all of env's variables
    if ARGS.list:
        if ARGS.file is not None:
            if filepath.is_dir():
                print(*filepath.iterdir())
                sys.exit()
        print(f"These are the aliases within env '{env}':")
        for key, val in full_data[env].items():
            print(f'"{key}": "{val}"')
        sys.exit(0)

    # Depending on which kind of file this is, output something to stdout
    if ARGS.output and ARGS.file is not None:
        if not filepath.exists():
            print("Not a valid file or directory")
            sys.exit(1)
        if filepath.is_file():
            echoFile(filepath)
        else:
            print(*os.listdir(filepath))
        sys.exit(0)

    # Adds keyword + file as an json key if it doesnt exist,
    # otherwise, update existing one
    if ARGS.add is not None and ARGS.file is not None:
        if not filepath.exists():
            sys.exit("Not a valid filepath, exiting.")

        alias = ARGS.add
        full_data[env][alias] = str(filepath)
        with open(main_data_file, "w") as f:
            f.seek(0)
            json.dump(full_data, f, indent=4)
            f.truncate()

        # If alias already exists in env
        update_alias = True if alias in full_data[env] else False
        if update_alias:
            print(f"Alias '{alias}' in env '{env}' updated successfully!")
        else:
            print(
                f"Alias '{alias}' added to environment '{env}' successfully!")
        sys.exit(0)

    # Removes alias from data file
    if ARGS.remove and ARGS.file is not None:
        with open(main_data_file, "r+") as f:
            if original_alias not in full_data[env]:
                sys.exit(f'Alias {original_alias} not found under env "{env}"')
            else:
                del full_data[env][original_alias]
                f.seek(0)
                json.dump(full_data, f, indent=4)
                f.truncate()
                print(f'Alias {original_alias} sucessfully removed from env {env}!')
                sys.exit(0)

    # if there's no file and there was no other option, print help
    # also, if nothing else than the file is specified, run --path
    if ARGS.file is not None:
        print(filepath)
        sys.exit(0)


if __name__ == '__main__':
    main()
