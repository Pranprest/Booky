"""
    Booky - A command line utility for bookmarking files

    ===
        Author: Pranprest
    ===
"""
import argparse
import json
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

    return _parser


def echoFile(FilePath: Path) -> None:
    import mmap
    from shutil import copyfileobj
    with open(FilePath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
            copyfileobj(s, sys.stdout.buffer)


def main() -> None:
    # Create json data file if does'nt exist (or is empty) and reference it in main_data_file
    currosslash = "\\" if (os.name == "nt") else "/"
    main_data_file = Path(
        f"{Path(__file__).parent.absolute()}{currosslash}data.json")
    del currosslash
    if not main_data_file.exists() or os.stat(main_data_file).st_size == 0:
        with open(main_data_file, 'w') as f:
            f.write("{}")

    # Parse the args!
    parser = argParser()
    args = parser.parse_args()
    env = args.env

    # Check if env is actually in there, if not, create new one.
    if isinstance(args.env, str):
        with open(main_data_file, "r+") as f:
            full_data = json.load(f)
            if env not in full_data:
                full_data[env] = {}
                f.seek(0)
                json.dump(full_data, f, indent=4)
                f.truncate()

    # If args.file is an alias, set it to the alias'es filepath
    # And make a variable called filepath
    original_alias = args.file
    if not args.file == None:
        # Share this single "read" call for other every argument
        with open(main_data_file, "r") as f:
            full_data = json.load(f)
        if args.file in full_data[env]:
            args.file = Path(full_data[env][args.file])
        else:
            args.file = Path(args.file)
        # If it somehow isn't an absolute path, make it absolute anyways
        filepath = args.file.absolute()

    # Mutulally exclusive arguments:

    # Print alias'es folder, if not, print all of env's variables
    if args.list == True:
        if args.file != None:
            if filepath.is_dir():
                print(*os.listdir(filepath))
                sys.exit()
        print(f"These are the aliases within env '{env}':")
        for key, val in full_data[env].items():
            print(f'"{key}": "{val}"')
        sys.exit(0)

    # Depending on which kind of file this is, output something to stdout
    if args.output == True and not args.file == None:
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
    if not args.add == None and not args.file == None:
        if not filepath.exists():
            print("Not a valid filepath, exiting.")
            sys.exit(1)

        alias = args.add
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
    if args.remove == True and not args.file == None:
        with open(main_data_file, "r+") as f:
            if not original_alias in full_data[env]:
                print(f'Alias {original_alias} not found under env "{env}"')
                sys.exit(1)
            else:
                del full_data[env][original_alias]
                f.seek(0)
                json.dump(full_data, f, indent=4)
                f.truncate()
                print(
                    f'Alias {original_alias} sucessfully removed from env "{env}"!')
                sys.exit(0)

    # if there's no file and there was no other option, print help
    # also, if nothing else than the file is specified, run --path
    if args.file == None:
        parser.print_help()
        sys.exit(0)
    else:
        print(filepath)


if __name__ == '__main__':
    main()
