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


def parseArgs(argv=None) -> argparse.ArgumentParser:
    _parser = argparse.ArgumentParser(
        description='Bookmark files and use them in other programs.', prog="Booky")

    # Manage bookmarks themselves
    _parser.add_argument('file',
                         type=str,
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

    return _parser.parse_args(argv)


def echoFile(FilePath: Path) -> None:
    import mmap
    from shutil import copyfileobj
    # TODO: Maybe implementing memory mapping to other places in this script would be good
    with open(FilePath, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as s:
            copyfileobj(s, sys.stdout.buffer)


def main() -> None:
    # Variable declaration
    currfilepath = Path(__file__).parent.absolute()
    currosslash = "\\" if (os.name == "nt") else "/"
    main_data_file = f"{currfilepath}{currosslash}data.json"
    del currosslash
    del currfilepath
    # Start handling args
    args = parseArgs()
    print(args)
    env = args.env

    # Firstly check if env exists
    if isinstance(args.env, str):
        # Check if env is actually in there, if not, create new one.
        with open(main_data_file, "r+") as f:
            full_data = json.load(f)
            if args.env not in full_data:
                full_data[args.env] = {}
                f.seek(0)
                json.dump(full_data, f, indent=4)
                f.truncate()

    # Check if file/folder is an alias
    # If so, make "args.file" be it's path
    with open(main_data_file, "r") as f:
        full_data = json.load(f)
    original_alias = args.file
    if args.file in full_data[env]:
        args.file = full_data[env][args.file]
    del full_data
    filepath = Path(args.file).absolute()
    if not filepath.exists():
        print("Not a valid file, directory or alias")
        sys.exit(1)

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

        with open(main_data_file, "r") as f:
            full_data = json.load(f)
        # If alias already exists in env
        update_alias = False
        if alias in full_data[env]:
            print(
                f"Alias '{alias}' already exists in env '{env}', updating...")
            update_alias = True
        full_data[env][alias] = f"{filepath}"

        with open(main_data_file, "w") as f:
            f.seek(0)
            json.dump(full_data, f, indent=4)
            f.truncate()

        if not update_alias:
            print(f"Alias '{alias}' in env '{env}' updated successfully!")
        else:
            print(
                f"Alias '{alias}' added to environment '{env}' successfully!")
        sys.exit(0)

    if args.remove == True:
        # FIXME: Works weirdly with non-default env aliases lol
        with open(main_data_file, "r+") as f:
            full_data = json.load(f)
            if not original_alias in full_data[env]:
                print(f'Alias not found under env "{env}"')
                sys.exit(1)
            del full_data[env][original_alias]
            f.seek(0)
            json.dump(full_data, f, indent=4)
            f.truncate()
        print(f'Alias {original_alias} sucessfully removed from env "{env}"!')


if __name__ == '__main__':
    # Weird workaround, but works pretty well!!
    if len(sys.argv) <= 1:
        sys.argv += "."
    if "-" in sys.argv[1]:
        sys.argv += "."
        sys.argv = [*sys.argv, sys.argv.pop(1)]
    main()
