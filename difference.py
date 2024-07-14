from transform import signed, multi_linear_transform, resized_to_shape, sign_unshifted_image, max_luminance
from patch import unpack
from cli import RESET, RED, GREEN, ORANGE, BLUE, MAGENTA, CYAN, BOLD
from traverse import check_out_path, print_indented

import cv2
import numpy as np
from pathlib import Path


SUFFIXES = [".png"] # FIXME: duplicate identifier


def scaled_stack(scale: np.ndarray, elements: list[np.ndarray]):
    return np.stack([scale * e for e in elements], axis=-1)


def create_difference_image(difference):
    flat_difference = difference[:,:,0] + difference[:,:,1] + difference[:,:,2] # ignore alpha (if exists)
    flat_difference_is_negative = flat_difference < 0
    flat_difference_is_positive = flat_difference > 0
    flat_difference_is_zero = flat_difference == 0
    max_lum = max_luminance(np.dtype(np.uint8 if difference.dtype == np.int16 else np.uint16))
    if abs_max := max(int(flat_difference.max()), abs(int(flat_difference.min()))):
        coefficient_index = 1 * flat_difference_is_positive + 2 * flat_difference_is_negative # flat_difference == 0 will have index 0
        transformed = multi_linear_transform(coefficient_index, flat_difference, [(0, 0), (-max_lum/abs_max, max_lum), (max_lum/abs_max, max_lum)])
        transformed = np.array(transformed, dtype=np.uint8)
        # positive_difference = multi_linear_transform(flat_difference_is_positive, flat_difference, [(0, max_lum)])
        # negative_difference = multi_linear_transform(flat_difference_is_negative, flat_difference, [(0, max_lum)])
        # black_channel = np.zeros(flat_difference.shape)
        white_channel = np.ones(flat_difference.shape) * max_lum
        positive_difference = scaled_stack(flat_difference_is_positive, [transformed, transformed, white_channel])
        negative_difference = scaled_stack(flat_difference_is_negative, [white_channel, transformed, transformed])
        zero_difference = scaled_stack(flat_difference_is_zero, [white_channel, white_channel, white_channel])
        # red_image_mask = np.zeros(difference.shape)
        # blue_image_mask = np.zeros(difference.shape)
        # red_image_mask[..., 0] = 1
        # blue_image_mask[..., 1] = 1
        # difference_image = zero_difference + red_image_mask * positive_difference + blue_image_mask * negative_difference
        difference_image = zero_difference + positive_difference + negative_difference
        return difference_image
    else:
        return np.ones(difference.shape) * max_lum


def compare_image(reference_path: Path, patched_path: Path, difference_path: Path|None = None) -> tuple[int, int]:
    reference_image = cv2.imread(reference_path, cv2.IMREAD_UNCHANGED)
    patched_image = cv2.imread(patched_path, cv2.IMREAD_UNCHANGED)
    resized_image = resized_to_shape(reference_image, patched_image.shape)
    
    patched: np.ndarray = patched_image.astype(np.int16 if patched_image.dtype == np.uint8 else np.int32)
    resized: np.ndarray = resized_image.astype(np.int16 if patched_image.dtype == np.uint8 else np.int32)
    difference = resized - patched
    if difference_path:
        difference_image = create_difference_image(difference)
        cv2.imwrite(difference_path.with_stem(f"{difference_path.stem}-{reference_path.stem}-{patched_path.stem}"), difference_image)
    return int(difference.min()), int(difference.max())


def compare_pack(reference_path: Path, patched_path: Path, difference_path: Path|None, print_full_path: bool = False) -> None:
    error_paths = []
    def callback_dir(path: Path, level: int):
        text = path.name
        if images := [p for p in path.iterdir() if p.is_file and p.suffix.lower() in SUFFIXES]:
            text += f" ({len(images)})" # TODO: /total
        print_indented(f"{BOLD}{MAGENTA}{text}{RESET}", level)
    def callback_file(image_reference_path: Path, level: int):
        if image_reference_path.suffix in SUFFIXES: # and image_reference_path.name == "bch-bench-wood.png":
            relative_replacements_path = image_reference_path.relative_to(reference_path)
            image_patched_path = patched_path.joinpath(relative_replacements_path)
            image_reference_path = reference_path.joinpath(relative_replacements_path)
            text = (image_reference_path if print_full_path else relative_replacements_path).as_posix()
            print_indented("… " + text, level, end=(None if reference_path == None else "\r"))
            try:
                if not image_patched_path.exists():
                    raise FileNotFoundError("Patched file does not exist")
                difference = compare_image(image_reference_path, image_patched_path)
                text2 = (f"{GREEN}✔{RESET}" if difference == (0, 0) else f"{RED}✖{RESET}") + " " + text + "\t" + f"({BLUE}{difference[0]}{RESET}, {RED}{difference[1]}{RESET})"
                print_indented(text2, level, end="\n", flush=True) # https://symbolsdb.com/check-mark-symbol
            except FileNotFoundError as e:
                print_indented(f"{ORANGE}✖{RESET} {text}", level, end="\t", flush=True)
                print("warning:", str(e))
            except Exception as e:
                error_paths.append(image_reference_path)
                print_indented(f"{RED}✖{RESET} {text}", level, end="\t", flush=True)
                print("error:", str(e))
                raise e
    check_out_path(reference_path, callback_dir, callback_file)
    if error_paths:
        print(f"Encountered {len(error_paths)} errors:")
        for path in error_paths:
            print("  " + str(path))


def reverse_original(modified_path: Path, patch_path: Path, reversed_path: Path) -> None:
    modified_image = cv2.imread(modified_path, cv2.IMREAD_UNCHANGED)
    patch_image = cv2.imread(patch_path, cv2.IMREAD_UNCHANGED)
    shifted_image, positive_maps = unpack(patch_image)
    difference_is_positive, hashed_is_positive = positive_maps

    shifted = shifted_image.astype(np.int16)
    hashed = sign_unshifted_image(hashed_is_positive, shifted)
    
    noise: np.ndarray = np.zeros(hashed.shape) # create_noise_image(resized, 0)
    difference = hashed + signed(difference_is_positive, noise)
    modified: np.ndarray = modified_image.astype(np.int16)
    resized = modified - difference
    reversed_image: np.ndarray = resized.astype(np.uint8)
    cv2.imwrite(reversed_path, reversed_image)