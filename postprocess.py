from pathlib import Path
import subprocess
from cli import RESET, RED, GREEN, ORANGE, BLUE, MAGENTA, CYAN, BOLD
from traverse import check_out_path, print_indented


SUFFIXES = [".png"]
DEFAULT_ORIGINAL_PLACEHOLDER  = "[:original:]"
DEFAULT_PROCESSED_PLACEHOLDER = "[:processed:]"


def run_command(command_template: str, image_original_path: Path, image_processed_path: Path, original_placeholder: str = DEFAULT_ORIGINAL_PLACEHOLDER, processed_placeholder: str = DEFAULT_PROCESSED_PLACEHOLDER) -> None:
    assert original_placeholder in command_template
    assert processed_placeholder in command_template
    command = command_template
    command = command.replace(original_placeholder, "'" + image_original_path.as_posix() + "'")
    command = command.replace(processed_placeholder, "'" + image_processed_path.as_posix() + "'")
    finished = subprocess.run(command)
    try:
        finished.check_returncode()
    except Exception as e:
        print()
        print(finished.returncode)
        print(repr(command_template))
        print(image_original_path)
        print(image_processed_path)
        print()
        raise e


def create_texture_processed_pack(command_template: str, original_path: Path, processed_path: Path, original_placeholder: str = DEFAULT_ORIGINAL_PLACEHOLDER, processed_placeholder: str = DEFAULT_PROCESSED_PLACEHOLDER, print_full_path: bool = False, overwrite: bool = False) -> None:
    error_paths = []
    def callback_dir(path: Path, level: int):
        text = path.name
        if images := [p for p in path.iterdir() if p.is_file and p.suffix.lower() in SUFFIXES]:
            text += f" ({len(images)})" # TODO: /total
        print_indented(f"{BOLD}{MAGENTA}{text}{RESET}", level)
    def callback_file(image_original_path: Path, level: int):
        if image_original_path.suffix in SUFFIXES: # and image_original_path.name == "bch-bench-wood.png":
            relative_replacements_path = image_original_path.relative_to(original_path)
            image_processed_path = processed_path.joinpath(relative_replacements_path)
            text = (image_original_path if print_full_path else relative_replacements_path).as_posix()
            print_indented("… " + text, level, end=(None if processed_path == None else "\r"))
            image_processed_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                if not overwrite and image_processed_path.exists():
                    raise FileExistsError("Not allowed to overwrite")
                run_command(command_template, image_original_path, image_processed_path, original_placeholder, processed_placeholder)
            except FileExistsError as e:
                print_indented(f"{GREEN}✖{RESET} {text} SKIPPED: {e}", level, end="\n", flush=True)
            # except FileExistsError as e:
            #     print_indented(f"{ORANGE}✖{RESET} {text}", level, end="\t", flush=True)
            #     print("warning:", str(e))
            except Exception as e:
                error_paths.append(image_original_path)
                print_indented(f"{RED}✖{RESET} {text}", level, end="\t", flush=True)
                print("error:", str(e))
                raise e
            else:
                print_indented(f"{GREEN}✔{RESET}", level, flush=True) # https://symbolsdb.com/check-mark-symbol
    check_out_path(original_path, callback_dir, callback_file)
    if error_paths:
        print(f"Encountered {len(error_paths)} errors:")
        for path in error_paths:
            print("  " + str(path))