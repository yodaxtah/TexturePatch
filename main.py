import argparse
from pathlib import Path

from patch import create_patch, create_patched
from difference import compare_image, reverse_original
from test import test_patch
from pack import create_texture_pack, create_texture_patch_pack


def create(original_path_str: str, modified_path_str: str, patch_path_str: str):
    original_path = Path(original_path_str)
    modified_path = Path(modified_path_str)
    patch_path = Path(patch_path_str)
    if original_path.is_file() and modified_path.is_file():
        create_patch(original_path, modified_path, patch_path)
    elif original_path.is_dir() and modified_path.is_dir():
        create_texture_patch_pack(original_path, modified_path, patch_path)
    else:
        print("Expected either all directories or all images")


def apply(original_path_str: str, patch_path_str: str, patched_path_str: str):
    original_path = Path(original_path_str)
    patch_path = Path(patch_path_str)
    patched_path = Path(patched_path_str)
    if original_path.is_file() and patch_path.is_file():
        create_patched(original_path, patch_path, patched_path)
    elif original_path.is_dir() and patch_path.is_dir():
        create_texture_pack(original_path, patch_path, patched_path)
    else:
        print("Expected either all directories or all images")


def diff(reference_path_str: str, patched_path_str: str, difference_path_str: str|None):
    reference_path = Path(reference_path_str)
    patched_path = Path(patched_path_str)
    difference_path = Path(difference_path_str) if difference_path_str else None
    if reference_path.is_file() and patched_path.is_file():
        print(compare_image(reference_path, patched_path, difference_path))
    elif reference_path.is_dir() and patched_path.is_dir():
        print("Directory comparison not implemented yet")
        pass
    else:
        print("Expected either all directories or all images")


def reverse(modified_path_str: str, patch_path_str: str, reversed_path_str: str|None):
    modified_path = Path(modified_path_str)
    patch_path = Path(patch_path_str)
    reversed_path = Path(reversed_path_str)
    # TODO: mk parents
    if modified_path.is_file() and patch_path.is_file():
        reverse_original(modified_path, patch_path, reversed_path)
    elif modified_path.is_dir() and patch_path.is_dir():
        print("Directory reversing not implemented yet")
        pass
    else:
        print("Expected either all directories or all images")


def test(original_path_str: str, modified_path_str: str):
    original_path = Path(original_path_str)
    modified_path = Path(modified_path_str)
    if original_path.is_file() and modified_path.is_file():
        test_patch(original_path, modified_path)
    elif original_path.is_dir() and modified_path.is_dir():
        pass
    else:
        print("Expected either all directories or all images")


def main():
    parser = argparse.ArgumentParser(prog="TexturePatch", description="Tool to create patches from the original image to the modified image")
    subparsers = parser.add_subparsers(dest="subparser_name", help="sub-command help")
    
    create_parser = subparsers.add_parser("create", help="Create a patch")
    create_parser.add_argument(dest="original_path",                metavar="original-path", type=str, # "-i", "--input", default=".",
        help="The path to the original directory or image")
    create_parser.add_argument(dest="modified_path",                metavar="modified-path", type=str, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")
    create_parser.add_argument(dest="patch_path",                   metavar="patch-path",    type=str, # "-o", "--output", default=DEFAULT_OUTPUT_PATH,
        help="The path to the directory containing patch images or patch image")
    # --print-from-root
    # -r --max-depth x

    apply_parser = subparsers.add_parser("apply", help="Apply a patch")
    apply_parser.add_argument(dest="original_path",                 metavar="original-path", type=str, # "-i", "--input", default=".",
        help="The path to the original directory or image")
    apply_parser.add_argument(dest="patch_path",                    metavar="patch-path",    type=str, # "-o", "--patch", default=DEFAULT_OUTPUT_PATH,
        help="The path to the patch directory or image")
    apply_parser.add_argument(dest="patched_path",                  metavar="patched-path",  type=str, # "-m", "--output", default=DEFAULT_OUTPUT_PATH,
        help="The path to the directory containing patched images or patched image")
    # --print-from-root
    # -r --max-depth x

    diff_parser = subparsers.add_parser("diff", help="Compare a reference image with a modified one")
    diff_parser.add_argument(dest="reference_path",                   metavar="reference-path",  type=str, # "-i", "--input", default=".",
        help="The path to the reference directory or image")
    diff_parser.add_argument(dest="modified_path",                  metavar="modified-path", type=str, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")
    diff_parser.add_argument(dest="difference_path",                      metavar="difference-path",     type=str, nargs="?", default=None,# "-o", "--output",
        help="The path to the directory containing difference images or difference image")

    reverse_parser = subparsers.add_parser("reverse", help="Reverse the original image by a patch")
    reverse_parser.add_argument(dest="modified_path",               metavar="modified-path", type=str, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")
    reverse_parser.add_argument(dest="patch_path",                  metavar="patch-path",    type=str, # "-o", "--output", default=DEFAULT_OUTPUT_PATH,
        help="The path to the patch directory or image")
    reverse_parser.add_argument(dest="reversed_path",               metavar="reversed-path", type=str, # "-i", "--input", default=".",
        help="The path to the directory containing reversed images or reversed image")

    test_parser = subparsers.add_parser("test", help="Run all modes on an original and its modified image")
    test_parser.add_argument(dest="original_path",               metavar="original-path", type=str, # "-i", "--input", default=".",
        help="The path to the original directory or image")
    test_parser.add_argument(dest="modified_path",               metavar="modified-path", type=str, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")

    arguments = parser.parse_args()
    command = arguments.subparser_name
    match command:
        case "create":  create(arguments.original_path, arguments.modified_path, arguments.patch_path)
        case "apply":   apply(arguments.original_path, arguments.patch_path, arguments.patched_path)
        case "diff":    diff(arguments.reference_path, arguments.modified_path, arguments.difference_path)
        case "reverse": reverse(arguments.modified_path, arguments.patch_path, arguments.reversed_path)
        case "test":    test(arguments.original_path, arguments.modified_path)
        case _:         parser.print_help()


if __name__ == "__main__":
    main()