from pathlib import Path
from typing import Callable #, Optional
from patch import create_patch, create_patched
from difference import compare_image


INDENTATION = "  " # "\t"
SUFFIXES = [".png"]

RESET = "\x1b[0m"
RED = "\x1b[1;31m"
GREEN = "\x1b[1;32m"
ORANGE = "\x1b[1;33m"
BLUE = "\x1b[1;34m"
MAGENTA = "\x1b[1;35m"
CYAN = "\x1b[1;36m"
BOLD = "\x1b[1;37m"


def print_indented(text: str, level: int, end: str|None = None, flush: str|None = None) -> None:
    print(INDENTATION * level + text, end=end, flush=flush)


def print_path_name_indented(path: Path, level: int, end: str|None = None, flush: str|None = None) -> None:
    print_indented(path.name, level, end=end, flush=flush)


def check_out_path(target_path: Path, callback_dir: Callable[[str, int], None], callback_file: Callable[[str, int], None], level: int = 0) -> None:
    """"
    This function recursively prints all contents of a pathlib.Path object
    """
    callback_dir(target_path, level)
    for child_path in target_path.iterdir():
        if child_path.is_dir():
            check_out_path(child_path, callback_dir, callback_file, level+1)
        else:
            callback_file(child_path, level+1)


def create_texture_patch_pack(original_path: Path, modified_path: Path, patch_path: Path) -> None:
    def callback_dir(path: Path, level: int):
        text = path.name
        if images := [p for p in path.iterdir() if p.is_file and p.suffix.lower() in SUFFIXES]:
            text += f" ({len(images)})"
        print_indented(f"{BOLD}{MAGENTA}{text}{RESET}", level)
    def callback_file(image_modified_path: Path, level: int):
        if image_modified_path.suffix in SUFFIXES: # and image_modified_path.name == "bch-bench-wood.png":
            uncommon_path = image_modified_path.relative_to(modified_path)
            image_patch_path = patch_path.joinpath(uncommon_path)
            image_original_path = original_path.joinpath(uncommon_path)
            text = image_original_path.as_posix()
            print_indented("… " + text, level, end=(None if modified_path == None else "\r"))
            image_patch_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                if not image_original_path.exists():
                    raise FileNotFoundError("Original file does not exist")
                create_patch(image_original_path, image_modified_path, image_patch_path)
            except FileNotFoundError as e:
                print_indented(f"{ORANGE}✖{RESET} {text}", level, end="\t", flush=True)
                print("warning:", str(e))
            except Exception as e:
                print_indented(f"{RED}✖{RESET} {text}", level, end="\t", flush=True)
                print("error:", str(e))
            else:
                print_indented(f"{GREEN}✔{RESET}", level, flush=True) # https://symbolsdb.com/check-mark-symbol
    check_out_path(modified_path, callback_dir, callback_file)


def create_texture_pack(original_path: Path, patch_path: Path, pack_path: Path, modified_path: Path|None = None) -> None:
    def callback_dir(path: Path, level: int):
        text = path.name
        if images := [p for p in path.iterdir() if p.is_file and p.suffix.lower() in SUFFIXES]:
            text += f" ({len(images)})"
        print_indented(f"{BOLD}{CYAN}{text}{RESET}", level)
    def callback_file(image_patch_path: Path, level: int):
        # if image_patch_path.suffix in SUFFIXES:
        uncommon_path = image_patch_path.relative_to(patch_path)
        image_pack_path = pack_path.joinpath(uncommon_path)
        image_original_path = original_path.joinpath(uncommon_path)
        text = image_pack_path.as_posix()
        print_indented("… " + text, level, end="\r")
        image_pack_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            create_patched(image_original_path, image_patch_path, image_pack_path)
            if modified_path:
                image_modified_path = modified_path.joinpath(uncommon_path)
                if (difference := compare_image(image_modified_path, image_pack_path)) == (0, 0):
                    print_indented(f"{GREEN}✔{RESET}", level, flush=True) # https://symbolsdb.com/check-mark-symbol
                else:
                    print_indented(f"{RED}✖{RESET} {text}", level, end="\t", flush=True)
                    print(f"({BLUE}{difference[0]}{RESET}, {RED}{difference[1]}{RESET})")
            else:
                print_indented(f"{GREEN}✔{RESET}", level, flush=True) # https://symbolsdb.com/check-mark-symbol
        except AssertionError as e:
            print_indented(f"{RED}✖{RESET} {text}", level, end="\t", flush=True)
            print("assertion error:", str(e))
        except Exception as e:
            print_indented(f"{RED}✖{RESET} {text}", level, end="\t", flush=True)
            print("error:", str(e))
    check_out_path(patch_path, callback_dir, callback_file)


if __name__ == "__main__":
    # create_texture_patch_pack(Path("./test/modified"), Path("./test/original"), Path("./test/patch"))
    # create_texture_pack(Path("./test/patch"), Path("./test/original"), Path("./test/pack"))
    create_texture_pack(Path("./test/patch"), Path("./test/original"), Path("./test/pack"), Path("./test/modified"))
