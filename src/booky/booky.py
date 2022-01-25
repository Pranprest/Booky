"""
    Booky - A command line utility for bookmarking files

    ===
        Author: Pranprest
    ===
"""
import argparse
import json
# import toml
from pathlib import Path
import sys
import os


def argParser() -> argparse.ArgumentParser:
    _parser = argparse.ArgumentParser(
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

    # TODO: Add "run" (run file)/"edit" (open code editor or whatever!)
    # (if that can actually be implemented)

    return _parser


def echoFile(FilePath: Path) -> None:
    import mmap
    from shutil import copyfileobj
    # TODO: Maybe implementing memory mapping to other places in this script would be good
    with open(FilePath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
            copyfileobj(s, sys.stdout.buffer)


def main() -> None:
    # Variable declaration
    currosslash = "\\" if (os.name == "nt") else "/"
    main_data_file = Path(
        f"{Path(__file__).parent.absolute()}{currosslash}data.json")
    del currosslash
    if not main_data_file.exists():
        with open(main_data_file, 'w') as f:
            f.write("{}")

    # Start handling args
    parser = argParser()
    args = parser.parse_args()
    env = args.env

    if isinstance(args.env, str):
        # Check if env is actually in there, if not, create new one.
        with open(main_data_file, "r+") as f:
            full_data = json.load(f)
            if args.env not in full_data:
                full_data[args.env] = {}
                f.seek(0)
                json.dump(full_data, f, indent=4)
                f.truncate()

    if not args.file == None:
        with open(main_data_file, "r") as f:
            full_data = json.load(f)
        original_alias = args.file
        if args.file in full_data[env]:
            args.file = full_data[env][args.file]
        del full_data
        filepath = Path(args.file).absolute()

    # Handle arguments properly now
    if args.list == True:
        # Literally just print everything under XYZ env
        with open(main_data_file, "r+") as f:
            full_data = json.load(f)
        print(f"These are the aliases within env '{env}':")
        for key, val in full_data[env].items():
            print(f'"{key}": "{val}"')
        sys.exit(0)

    if args.path == True:
        if not filepath.exists():
            print("Not a valid file or directory")
            sys.exit(1)
        print(filepath)

    if args.output == True:
        if not filepath.exists():
            print("Not a valid file or directory")
            sys.exit(1)
        if filepath.is_file():
            echoFile(filepath)
        else:
            print(*os.listdir(filepath))
        sys.exit(0)

    if not args.add == None:
        alias = args.add
        if not filepath.exists():
            print("Not a valid filepath, exiting.")
            sys.exit(1)
        with open(main_data_file, "r") as f:
            full_data = json.load(f)
        # If alias already exists in env
        update_alias = False
        if alias in full_data[env]:
            update_alias = True
        full_data[env][alias] = f"{filepath}"

        with open(main_data_file, "w") as f:
            f.seek(0)
            json.dump(full_data, f, indent=4)
            f.truncate()

        if update_alias:
            print(f"Alias '{alias}' in env '{env}' updated successfully!")
        else:
            print(
                f"Alias '{alias}' added to environment '{env}' successfully!")
        sys.exit(0)

    if args.remove == True:
        with open(main_data_file, "r+") as f:
            full_data = json.load(f)
            if not original_alias in full_data[env]:
                print(f'Alias {original_alias} not found under env "{env}"')
                sys.exit(1)
            del full_data[env][original_alias]
            f.seek(0)
            json.dump(full_data, f, indent=4)
            f.truncate()
        print(f'Alias {original_alias} sucessfully removed from env "{env}"!')
        sys.exit(0)

    # if there's no file and there was no other option, print help
    if args.file == None:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()
