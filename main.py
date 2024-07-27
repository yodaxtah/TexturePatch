import argparse
from pathlib import Path

from patch import create_patch, create_patched, filter_image
from difference import compare_image, compare_pack, reverse_original
from test import test_patch
from pack import create_texture_pack, create_texture_patch_pack
from filters import FITLER_NAMES
from postprocess import run_command, create_texture_processed_pack


def create(original_path: Path, modified_path: Path, patch_path: Path, filter_names: list[str] = [], print_full_path: bool = False):
    if not original_path.exists():
        print(original_path, "does not exist")
    elif not modified_path.exists():
        print(modified_path, "does not exist")
    elif original_path == patch_path:
        print(original_path, "will be overwritten because the same path is provided")
    elif modified_path == patch_path:
        print(modified_path, "will be overwritten because the same path is provided")
    elif original_path.is_file() and modified_path.is_file():
        create_patch(original_path, modified_path, patch_path, filter_names)
    elif original_path.is_dir() and modified_path.is_dir():
        create_texture_patch_pack(original_path, modified_path, patch_path, filter_names, print_full_path)
    else:
        print("Expected either all directories or all images")
        print(original_path, "is a", "file" if original_path.is_file() else "", "directory" if original_path.is_dir() else "")
        print(modified_path, "is a", "file" if modified_path.is_file() else "", "directory" if modified_path.is_dir() else "")


def apply(original_path: Path, patch_path: Path, patched_path: Path, valide_path: Path|None, filter_names: list[str] = [], print_full_path: bool = False):
    if not original_path.exists():
        print(original_path, "does not exist")
    elif not patch_path.exists():
        print(patch_path, "does not exist")
    elif valide_path and not valide_path.exists():
        print(valide_path, "does not exist")
    elif original_path == patched_path:
        print(original_path, "will be overwritten because the same path is provided")
    elif patch_path == patched_path:
        print(patch_path, "will be overwritten because the same path is provided")
    elif original_path.is_file() and patch_path.is_file():
        if valide_path:
            print("compare not setup for single images yet")
        create_patched(original_path, patch_path, patched_path, filter_names)
    elif original_path.is_dir() and patch_path.is_dir():
        create_texture_pack(original_path, patch_path, patched_path, valide_path, filter_names, print_full_path)
    else:
        print("Expected either all directories or all images")
        print(original_path, "is a", "file" if original_path.is_file() else "", "directory" if original_path.is_dir() else "")
        print(patch_path,    "is a", "file" if patch_path.is_file() else "",    "directory" if patch_path.is_dir() else "")


def diff(reference_path: Path, patched_path: Path, difference_path: Path|None, print_full_path: bool = False):
    if not reference_path.exists():
        print(reference_path, "does not exist")
    elif not patched_path.exists():
        print(patched_path, "does not exist")
    elif reference_path.is_file() and patched_path.is_file():
        print(compare_image(reference_path, patched_path, difference_path))
    elif reference_path.is_dir() and patched_path.is_dir():
        compare_pack(reference_path, patched_path, difference_path, print_full_path)
    else:
        print("Expected either all directories or all images")
        print(reference_path, "is a", "file" if reference_path.is_file() else "", "directory" if reference_path.is_dir() else "")
        print(patched_path,   "is a", "file" if patched_path.is_file() else "",   "directory" if patched_path.is_dir() else "")


def reverse(modified_path: Path, patch_path: Path, reversed_path: Path|None):
    if not modified_path.exists():
        print(modified_path, "does not exist")
    elif not patch_path.exists():
        print(patch_path, "does not exist")
    elif modified_path == patched_path:
        print(modified_path, "will be overwritten because the same path is provided")
    elif patch_path == patched_path:
        print(patch_path, "will be overwritten because the same path is provided")
    elif modified_path.is_file() and patch_path.is_file():
        reverse_original(modified_path, patch_path, reversed_path)
    elif modified_path.is_dir() and patch_path.is_dir():
        print("Directory reversing not implemented yet")
        pass
    else:
        print("Expected either all directories or all images")
        print(modified_path, "is a", "file" if modified_path.is_file() else "", "directory" if modified_path.is_dir() else "")
        print(patch_path,    "is a", "file" if patch_path.is_file() else "",    "directory" if patch_path.is_dir() else "")


def test(original_path: Path, modified_path: Path):
    if not original_path.exists():
        print(original_path, "does not exist")
    elif not modified_path.exists():
        print(modified_path, "does not exist")
    elif original_path.is_file() and modified_path.is_file():
        test_patch(original_path, modified_path)
    elif original_path.is_dir() and modified_path.is_dir():
        pass
    else:
        print("Expected either all directories or all images")
        print(original_path, "is a", "file" if original_path.is_file() else "", "directory" if original_path.is_dir() else "")
        print(modified_path, "is a", "file" if modified_path.is_file() else "", "directory" if modified_path.is_dir() else "")


def test_filter(image_path: Path, filtered_path: Path, fitler_names: list[str], seed_image_path: Path|None, inverted: bool = False):
    seed_image_path_ = seed_image_path if seed_image_path else image_path
    if not seed_image_path and inverted:
        print("warning: inverting filters while no seed provided. Are you sure you want to use the first path as seed? Ensure the same seed is used as when the filters were applied.")
    if not image_path.exists():
        print(image_path, "does not exist")
    elif not filtered_path.exists():
        print(filtered_path, "does not exist")
    elif not seed_image_path.exists():
        print(seed_image_path, "does not exist")
    elif image_path == filtered_path:
        print(filtered_path, "will be overwritten because the same path is provided")
    elif image_path.is_file() and filtered_path.is_file():
        filter_image(image_path, filtered_path, seed_image_path_, fitler_names, inverted)
    elif image_path.is_dir() and filtered_path.is_dir():
        print("Directory reversing not implemented yet")
        pass
    else:
        print("Expected either all directories or all images")
        print(image_path,    "is a", "file" if image_path.is_file() else "",    "directory" if image_path.is_dir() else "")
        print(filtered_path, "is a", "file" if filtered_path.is_file() else "", "directory" if filtered_path.is_dir() else "")


def process(command_template: str, original_path: Path, processed_path: Path, original_placeholder: str, processed_placeholder: str, print_full_path: bool = False):
    if not original_path.exists():
        print(original_path, "does not exist")
    elif original_placeholder not in command_template:
        print(f"template {repr(command_template)} is missing input placeholder {repr(original_placeholder)}")
    elif processed_placeholder not in command_template:
        print(f"template {repr(command_template)} is missing output placeholder {repr(processed_placeholder)}")
    elif original_path.is_file():
        run_command(command_template, original_path, processed_path, original_placeholder, processed_placeholder)
    elif original_path.is_dir():
        create_texture_processed_pack(command_template, original_path, processed_path, original_placeholder, processed_placeholder, print_full_path)
    else:
        print("Hm, this is impossible")


def main():
    parser = argparse.ArgumentParser(prog="TexturePatch", description="Tool to create patches from the original image to the modified image")
    subparsers = parser.add_subparsers(dest="subparser_name", help="sub-command help")
    
    create_parser = subparsers.add_parser("create", help="Create a patch")
    create_parser.add_argument(dest="original_path",                   metavar="original-path", type=Path, # "-i", "--input", default=".",
        help="The path to the original directory or image")
    create_parser.add_argument(dest="modified_path",                   metavar="modified-path", type=Path, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")
    create_parser.add_argument(dest="patch_path",                      metavar="patch-path",    type=Path, # "-o", "--output", default=DEFAULT_OUTPUT_PATH,
        help="The path to the directory containing patch images or patch image")
    create_parser.add_argument("-f", "--filters", dest="filter_names", metavar="filters-names", type=str, nargs="+", choices=FITLER_NAMES, default=[],
        help="The names of the filters to apply")
    create_parser.add_argument("--print-full-path", dest="print_full_path", action="store_true",
        help="Print full paths when processing an image in a directory")
    # -r --max-depth x

    apply_parser = subparsers.add_parser("apply", help="Apply a patch")
    apply_parser.add_argument(dest="original_path",                    metavar="original-path", type=Path, # "-i", "--input", default=".",
        help="The path to the original directory or image")
    apply_parser.add_argument(dest="patch_path",                       metavar="patch-path",    type=Path, # "-o", "--patch", default=DEFAULT_OUTPUT_PATH,
        help="The path to the patch directory or image")
    apply_parser.add_argument(dest="patched_path",                     metavar="patched-path",  type=Path, # "-m", "--output", default=DEFAULT_OUTPUT_PATH,
        help="The path to the directory containing patched images or patched image")
    apply_parser.add_argument("-v", "--validate", dest="validate_path", metavar="validate-path", type=Path,
        help="Validate the patched path result with another path's content")
    apply_parser.add_argument("-f", "--filters", dest="filter_names",  metavar="filters-names", type=str, nargs="+", choices=FITLER_NAMES, default=[],
        help="The names of the filters to invert")
    apply_parser.add_argument("--print-full-path", dest="print_full_path", action="store_true",
        help="Print full paths when processing an image in a directory")
    # -r --max-depth x

    diff_parser = subparsers.add_parser("diff", help="Compare a reference image with a modified one")
    diff_parser.add_argument(dest="reference_path",                    metavar="reference-path",  type=Path, # "-i", "--input", default=".",
        help="The path to the reference directory or image")
    diff_parser.add_argument(dest="modified_path",                     metavar="modified-path",   type=Path, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")
    diff_parser.add_argument(dest="difference_path",                   metavar="difference-path", type=Path, nargs="?", default=None,# "-o", "--output",
        help="The path to the directory containing difference images or difference image")
    diff_parser.add_argument("--print-full-path", dest="print_full_path", action="store_true",
        help="Print full paths when processing an image in a directory")

    reverse_parser = subparsers.add_parser("reverse", help="Reverse the original image by a patch")
    reverse_parser.add_argument(dest="modified_path",                  metavar="modified-path",   type=Path, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")
    reverse_parser.add_argument(dest="patch_path",                     metavar="patch-path",      type=Path, # "-o", "--output", default=DEFAULT_OUTPUT_PATH,
        help="The path to the patch directory or image")
    reverse_parser.add_argument(dest="reversed_path",                  metavar="reversed-path",   type=Path, # "-i", "--input", default=".",
        help="The path to the directory containing reversed images or reversed image")

    test_parser = subparsers.add_parser("test", help="Run all modes on an original and its modified image")
    test_parser.add_argument(dest="original_path",                     metavar="original-path",   type=Path, # "-i", "--input", default=".",
        help="The path to the original directory or image")
    test_parser.add_argument(dest="modified_path",                     metavar="modified-path",   type=Path, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the modified directory or image")

    filter_parser = subparsers.add_parser("test-filter", help=" all modes on an original and its modified image")
    filter_parser.add_argument(dest="image_path",                      metavar="image-path",      type=Path, # "-i", "--input", default=".",
        help="The path to the directory of images or image")
    filter_parser.add_argument(dest="filtered_path",                   metavar="filtered-path",   type=Path, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the filtered directory or image")
    filter_parser.add_argument(dest="filter_names",                    metavar="filters",         type=str, nargs="+", choices=FITLER_NAMES,
        help="The names of the filters to apply")
    filter_parser.add_argument("-s", "--seed", dest="seed_image_path", metavar="seed-image-path", type=Path, default=None,
        help="The path to the image that is used as a seed")
    filter_parser.add_argument("-i", "--inverted", dest="inverted",    action="store_true",
        help="Invert the filters and their order")
    # filter_parser.add_argument("--show",                  action="store_true",
    #     help="Enable verbose output")

    process_parser = subparsers.add_parser("process", help="Process a generic command on an image or directory")
    process_parser.add_argument(dest="command_template",                            metavar="command-template", type=str, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The command to execute containing placeholder-input and placeholder-output")
    process_parser.add_argument(dest="image_path",                                  metavar="image-path",       type=Path, # "-i", "--input", default=".",
        help="The path to the directory of images or image")
    process_parser.add_argument(dest="processed_path",                              metavar="processed-path",   type=Path, # "-m", "--modified", default=DEFAULT_OUTPUT_PATH,
        help="The path to the processed directory or image")
    process_parser.add_argument("--input-placeholder", dest="original_placeholder", metavar="original",  type=str, default="[:original:]",
        help="Use a different place holder in the command template for the image's input path")
    process_parser.add_argument("--output-placeholder", dest="processed_placeholder", metavar="processed", type=str, default="[:processed:]",
        help="Use a different place holder in the command template for the processed image's output path")
    process_parser.add_argument("--print-full-path", dest="print_full_path", action="store_true",
        help="Print full paths when processing an image in a directory")
    

    arguments = parser.parse_args()
    command = arguments.subparser_name
    match command:
        case "create":      create(arguments.original_path, arguments.modified_path, arguments.patch_path, arguments.filter_names, arguments.print_full_path)
        case "apply":       apply(arguments.original_path, arguments.patch_path, arguments.patched_path, arguments.validate_path, arguments.filter_names, arguments.print_full_path)
        case "diff":        diff(arguments.reference_path, arguments.modified_path, arguments.difference_path, arguments.print_full_path)
        case "reverse":     reverse(arguments.modified_path, arguments.patch_path, arguments.reversed_path)
        case "test":        test(arguments.original_path, arguments.modified_path)
        case "test-filter": test_filter(arguments.image_path, arguments.filtered_path, arguments.filter_names, arguments.seed_image_path, arguments.inverted)
        case "process":     process(arguments.command_template, arguments.image_path, arguments.processed_path, arguments.original_placeholder, arguments.processed_placeholder, arguments.print_full_path)
        case _:             parser.print_help()


if __name__ == "__main__":
    main()