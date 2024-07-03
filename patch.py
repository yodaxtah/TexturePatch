from transform import signed, sign_shifted_image, sign_unshifted_image, remainder_ceil, remainder_modulo, resized_to_shape

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
    return seed % (2**32 - 1)


def create_noise_image(image: np.ndarray, variance: float = 20) -> np.ndarray:
    assert variance in range(0,256)
    height, width, _ = image.shape
    np.random.seed(seed=extract_seed(image))
    noise = np.random.rand(*image.shape) * variance
    if noise.shape[2] > 3:
        noise[:,:,3] = 0
    return noise.astype(np.uint8)


def pack(image: np.ndarray, positive_maps: list[np.ndarray]):
    assert all([image.shape == m.shape for m in positive_maps])
    packed = image.reshape(-1)
    packed_shape = np.array(image.shape, dtype=np.uint16).view(dtype=np.uint8)
    for m in positive_maps:
        packed_map = np.packbits(m.reshape(-1))
        packed = np.append(packed, packed_map)
    row_size = np.prod(image.shape[1:])
    assert packed_map.size > row_size
    packed_number_of_zeros_size = 2
    number_of_zeros = remainder_modulo(packed.size + packed_number_of_zeros_size + packed_shape.size, row_size)
    packed = np.append(packed, np.zeros(number_of_zeros, dtype=np.uint8))
    packed = np.append(packed, np.array([number_of_zeros], dtype=np.uint16).view(dtype=np.uint8))
    packed = np.append(packed, packed_shape)
    packed_image = packed.reshape(-1, *image.shape[1:])
    return packed_image
# 144504
# 18063
# 648
# 156
# 6
# 180792

# 180792 == 144504 + 18063 * 2 + 156 + 6
# 6
# ?
# 648
# 144504
# 


def unpack(packed_image: np.ndarray):
    PACKED_SHAPE_SIZE = 6
    ZEROS_SIZE = 2
    packed = packed_image.reshape(-1)
    shape = tuple(packed[-PACKED_SHAPE_SIZE:].reshape(-1).view(dtype=np.uint16))
    number_of_zeros = int(packed[-PACKED_SHAPE_SIZE-ZEROS_SIZE:-PACKED_SHAPE_SIZE].reshape(-1).view(dtype=np.uint16))
    image_size = np.prod(shape)
    image = packed[:image_size].reshape(shape)
    # row_size = np.prod(shape[1:])
    tail_size = number_of_zeros + ZEROS_SIZE + PACKED_SHAPE_SIZE
    total_map_size = packed.size - image_size - tail_size
    number_of_positive_maps = total_map_size * 8 // image_size
    map_size = total_map_size // number_of_positive_maps
    assert number_of_positive_maps == 2
    positive_maps = []
    for i in range(number_of_positive_maps):
        offset = image_size + i * map_size
        unpacked_map = np.unpackbits(packed[offset:offset + map_size]).reshape(shape).astype(bool)
        positive_maps.append(unpacked_map)
    return image, positive_maps


def create_patch(original_path: Path, modified_path: Path, patch_path: Path):
    original_image = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
    modified_image = cv2.imread(modified_path, cv2.IMREAD_UNCHANGED)
    resized_image = resized_to_shape(original_image, modified_image.shape)

    resized: np.ndarray = resized_image.astype(np.int16)
    modified: np.ndarray = modified_image.astype(np.int16)
    noise: np.ndarray = create_noise_image(resized, NOISE_VARIANCE)
    difference: np.ndarray = modified - resized
    difference_is_positive: np.ndarray = difference >= 0

    hashed: np.ndarray = difference - signed(difference_is_positive, noise)
    hashed_is_positive: np.ndarray = hashed >= 0
    shifted: np.ndarray = sign_shifted_image(hashed)

    assert shifted.max() < 256
    assert shifted.min() >= 0

    shifted_image: np.ndarray = shifted.astype(np.uint8)
    patch_image: np.ndarray = pack(shifted_image, [difference_is_positive, hashed_is_positive])
    cv2.imwrite(patch_path, patch_image)


def create_patched(original_path: Path, patch_path: Path, patched_path: Path):
    patch_image = cv2.imread(patch_path, cv2.IMREAD_UNCHANGED)
    shifted_image, positive_maps = unpack(patch_image)
    difference_is_positive, hashed_is_positive = positive_maps
    original_image = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
    resized_image = resized_to_shape(original_image, shifted_image.shape)

    shifted = shifted_image.astype(np.int16)
    hashed = sign_unshifted_image(hashed_is_positive, shifted)

    resized: np.ndarray = resized_image.astype(np.int16)
    noise: np.ndarray = create_noise_image(resized, NOISE_VARIANCE)
    difference = hashed + signed(difference_is_positive, noise)
    patched: np.ndarray = difference + resized

    patched_image: np.ndarray = patched.astype(np.int16)
    cv2.imwrite(patched_path, patched_image)
