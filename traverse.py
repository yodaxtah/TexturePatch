from pathlib import Path
from typing import Callable #, Optional


INDENTATION = "  " # "\t"


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


if __name__ == "__main__":
    check_out_path(Path("./test/modified"), print_path_name_indented, print_path_name_indented)