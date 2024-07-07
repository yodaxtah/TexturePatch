from transform import signed, sign_shifted_image, sign_unshifted_image, remainder_ceil, remainder_modulo, resized_to_shape, max_luminance

import cv2
import numpy as np
from pathlib import Path


NOISE_VARIANCE = 96


def extract_seed(image: np.ndarray) -> np.ndarray:
    height, width, number_of_channels = [int(i) for i in image.shape]
    minimum = int(image.min())
    maximum = int(image.max())
    summation = int(image.sum())
    sample_sum1 = int(image.reshape(-1)[0::17].sum()) # https://stackoverflow.com/questions/25876640/subsampling-every-nth-entry-in-a-numpy-array
    sample_sum2 = int(image.reshape(-1)[1::23].sum()) # https://stackoverflow.com/questions/25876640/subsampling-every-nth-entry-in-a-numpy-array
    seed = width * height * (maximum - minimum) + summation - sample_sum1 * number_of_channels - sample_sum2
    return seed


def create_noise_image(image: np.ndarray, variance: float = 20) -> np.ndarray:
    assert variance in range(0, max_luminance(image)+1), "variance not in image range"
    height, width, _ = image.shape
    np.random.seed(seed=extract_seed(image) % max_luminance(np.dtype(np.uint32)))
    noise = np.random.rand(*image.shape) * variance * (1 if image.dtype == np.int16 else 256)
    if noise.shape[2] > 3:
        noise[:,:,3] = 0
    return noise.astype(np.uint8 if image.dtype == np.int16 else np.uint16)


def pack(image: np.ndarray, positive_maps: list[np.ndarray]):
    assert all([image.shape == m.shape for m in positive_maps]), "different map-image shapes"
    pixel_type = image.dtype
    footer_type = np.dtype(np.uint16)
    packed = image.reshape(-1)
    packed_shape = np.array(image.shape, dtype=footer_type).view(dtype=pixel_type)
    is_padded = False
    for m in positive_maps:
        packed_map = np.packbits(m.reshape(-1)).view(dtype=pixel_type)
        packed = np.append(packed, packed_map)
        BOOLEANS_IN_BYTE = 8
        if (unpacked_size := (packed_map.size * BOOLEANS_IN_BYTE)) > (expected_size := np.prod(m.shape)):
            if unpacked_size < expected_size + BOOLEANS_IN_BYTE:
                is_padded |= True
            else:
                raise RuntimeError("Unexpected size")
    row_size = np.prod(image.shape[1:])
    assert packed_map.size > row_size, "map is smaller than row"
    packed_number_of_zeros_size = footer_type.itemsize // pixel_type.itemsize
    is_padded_size = pixel_type.itemsize // pixel_type.itemsize
    number_of_zeros = remainder_modulo(packed.size + packed_number_of_zeros_size + is_padded_size + packed_shape.size, row_size)
    packed = np.append(packed, np.zeros(number_of_zeros, dtype=pixel_type))
    packed = np.append(packed, np.array([is_padded], dtype=pixel_type))
    packed = np.append(packed, np.array([number_of_zeros], dtype=footer_type).view(dtype=pixel_type))
    packed = np.append(packed, packed_shape)
    packed_image = packed.reshape(-1, *image.shape[1:])
    return packed_image


def unpack(packed_image: np.ndarray):
    pixel_type = packed_image.dtype
    footer_type = np.dtype(np.uint16)
    BOOLEANS_IN_BYTE = 8
    packed_shape_size = 3 * (footer_type.itemsize // pixel_type.itemsize)
    zeros_size = footer_type.itemsize // pixel_type.itemsize
    is_padded_size = pixel_type.itemsize // pixel_type.itemsize
    packed = packed_image.reshape(-1)
    offset = 0
    shape = tuple(packed[-offset-packed_shape_size:].reshape(-1).view(dtype=footer_type))
    offset += packed_shape_size
    number_of_zeros = int(packed[-offset-zeros_size:-offset].reshape(-1).view(dtype=footer_type))
    offset += zeros_size
    is_padded = bool(packed[-offset-is_padded_size:-offset].reshape(-1))
    image_size = np.prod(shape)
    image = packed[:image_size].reshape(shape)
    # row_size = np.prod(shape[1:])
    tail_size = number_of_zeros + is_padded_size + zeros_size + packed_shape_size
    total_map_size = packed.size - image_size - tail_size
    number_of_positive_maps = total_map_size * pixel_type.itemsize * BOOLEANS_IN_BYTE // image_size
    map_size = total_map_size // number_of_positive_maps
    assert number_of_positive_maps == 2, "expecting 2 maps for now"
    positive_maps = []
    for i in range(number_of_positive_maps):
        offset = image_size + i * map_size
        bits = np.unpackbits(packed[offset:offset + map_size].view(np.uint8))
        if is_padded:
            bits = bits[:-(bits.size % image_size)] # assumed shape of the map
        unpacked_map = bits.reshape(shape).astype(bool)
        positive_maps.append(unpacked_map)
    return image, positive_maps


def create_patch(original_path: Path, modified_path: Path, patch_path: Path):
    original_image = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
    modified_image = cv2.imread(modified_path, cv2.IMREAD_UNCHANGED) # for some reason 65535
    resized_image = resized_to_shape(original_image, modified_image.shape)

    resized: np.ndarray = resized_image.astype(np.int16 if modified_image.dtype == np.uint8 else np.int32) # FIXME
    modified: np.ndarray = modified_image.astype(np.int16 if modified_image.dtype == np.uint8 else np.int32) # FIXME
    noise: np.ndarray = create_noise_image(resized, NOISE_VARIANCE)
    difference: np.ndarray = modified - resized
    difference_is_positive: np.ndarray = difference >= 0

    hashed: np.ndarray = difference - signed(difference_is_positive, noise)
    hashed_is_positive: np.ndarray = hashed >= 0
    shifted: np.ndarray = sign_shifted_image(hashed)

    assert shifted.max() < max_luminance(modified_image) + 1, "image has too large value"
    assert shifted.min() >= 0, "image has too small value"

    shifted_image: np.ndarray = shifted.astype(modified_image.dtype)
    patch_image: np.ndarray = pack(shifted_image, [difference_is_positive, hashed_is_positive])
    cv2.imwrite(patch_path, patch_image)


def create_patched(original_path: Path, patch_path: Path, patched_path: Path):
    patch_image = cv2.imread(patch_path, cv2.IMREAD_UNCHANGED)
    shifted_image, positive_maps = unpack(patch_image)
    difference_is_positive, hashed_is_positive = positive_maps
    original_image = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
    resized_image = resized_to_shape(original_image, shifted_image.shape)

    shifted = shifted_image.astype(np.int16 if shifted_image.dtype == np.uint8 else np.int32)
    hashed = sign_unshifted_image(hashed_is_positive, shifted)

    resized: np.ndarray = resized_image.astype(np.int16 if shifted_image.dtype == np.uint8 else np.int32)
    noise: np.ndarray = create_noise_image(resized, NOISE_VARIANCE)
    difference = hashed + signed(difference_is_positive, noise)
    patched: np.ndarray = difference + resized

    assert patched.max() < max_luminance(patch_image) + 1, "image has too large value"
    assert patched.min() >= 0, "image has too small value"

    patched_image: np.ndarray = patched.astype(shifted_image.dtype)
    # patched_image[:,:,3] = 0
    cv2.imwrite(patched_path, patched_image)
