import cv2
import numpy as np
import math
import pathlib


Path = pathlib.Path


NOISE_VARIANCE = 96


def resized_to_shape(image: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    # height = shape[0] / image.shape[0]
    # width = shape[1] / image.shape[1]
    # resized_shape = (width, height)
    shape_ = (shape[1], shape[0])
    return cv2.resize(image, shape_, interpolation=cv2.INTER_CUBIC)


def extract_seed(image: np.ndarray) -> np.ndarray:
    height, width, number_of_channels = image.shape
    minimum = image.min()
    maximum = image.max()
    summation = image.sum()
    sample_sum = image.reshape(-1)[0::17].sum() # https://stackoverflow.com/questions/25876640/subsampling-every-nth-entry-in-a-numpy-array
    seed = width * height * (maximum - minimum) + summation + sample_sum + number_of_channels
    return seed


def create_noise_image(image: np.ndarray, variance: float = 20) -> np.ndarray:
    assert variance in range(0,256)
    height, width, _ = image.shape
    np.random.seed(seed=extract_seed(image))
    noise = np.random.rand(*image.shape) * variance
    noise[:,:,3] = 0
    return noise.astype(np.uint8)


def linear_transform(x: np.ndarray, a: int|float|np.ndarray, b: int|float|np.ndarray):
    return a * x + b


def multi_linear_transform(coefficient_index: np.ndarray, x: np.ndarray, coefficients: list[tuple[int, int]]) -> np.ndarray:
    assert coefficient_index.shape == x.shape
    transform = np.zeros(x.shape)
    for i in range(len(coefficients)):
        a, b = coefficients[i]
        transform += linear_transform(x, a, b) * (coefficient_index == i)
    return transform


def negative_transform(x: np.ndarray, coefficients: tuple[int, int]) -> np.ndarray:
    is_negative: np.ndarray = x < 0
    return multi_linear_transform(is_negative, x, [(1, 0), coefficients])


def sign_shifted_image(image: np.ndarray) -> np.ndarray:
    return negative_transform(image, (1, 256))


def absolute_image(image: np.ndarray) -> np.ndarray:
    return negative_transform(image, (-1, -1))


def sign_unshifted_image(is_positive: np.ndarray, image: np.ndarray) -> np.ndarray:
    return multi_linear_transform(np.invert(is_positive), image, [(1, 0), (1, -256)])


def signed(is_positive: np.ndarray, matrix: np.ndarray, positive_offset: int = 0, negative_offset: int = 0, positive_factor: int = 1, negative_factor: int = -1) -> np.ndarray:
    assert is_positive.shape == matrix.shape
    positive = (matrix + positive_offset) * positive_factor * is_positive
    negative = (matrix + negative_offset) * negative_factor * np.invert(is_positive)
    return positive + negative


def remainder_modulo(value: int, modulo: int) -> int:
    remainder = value % modulo
    if remainder == 0:
        return 0
    else:
        return modulo - remainder


def remainder_ceil(value: int, ceil: int) -> int:
    return math.ceil(value / ceil) * ceil


def pack(image: np.ndarray, positive_maps: list[np.ndarray]):
    assert all([image.shape == m.shape for m in positive_maps])
    packed = image.reshape(-1)
    packed_shape = np.array(image.shape, dtype=np.uint16).view(dtype=np.uint8)
    for m in positive_maps:
        packed_map = np.packbits(m.reshape(-1))
        packed = np.append(packed, packed_map)
    row_size = np.prod(image.shape[1:])
    number_of_zeros = remainder_modulo(packed.size + packed_shape.size, row_size)
    packed = np.append(packed, np.zeros(number_of_zeros))
    packed = np.append(packed, packed_shape)
    packed_image = packed.reshape(-1, *image.shape[1:])
    return packed_image


def unpack(packed_image: np.ndarray):
    PACKED_SHAPE_SIZE = 6
    packed = packed_image.reshape(-1)
    packed_shape = tuple(packed[-PACKED_SHAPE_SIZE:].reshape(-1).view(dtype=np.uint16))
    image_size = np.prod(packed_shape)
    image = packed[:image_size].reshape(packed_shape)
    row_size = np.prod(packed_shape[1:])
    last_row_size = remainder_ceil(PACKED_SHAPE_SIZE, row_size) # this was unnecessary
    total_map_size = (packed.size - image_size - last_row_size)
    number_of_positive_maps = total_map_size * 8 // image_size
    map_size = total_map_size // number_of_positive_maps
    assert number_of_positive_maps == 2
    positive_maps = []
    for i in range(number_of_positive_maps):
        offset = image_size + i * map_size
        unpacked_map = np.unpackbits(packed[offset:offset + map_size]).reshape(packed_shape).astype(bool)
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


def compare_image(reference_path: Path, patched_path: Path) -> None:
    reference_image = cv2.imread(reference_path, cv2.IMREAD_UNCHANGED)
    patched_image = cv2.imread(patched_path, cv2.IMREAD_UNCHANGED)
    resized_image = resized_to_shape(reference_image, patched_image.shape)
    
    patched: np.ndarray = patched_image.astype(np.int16)
    resized: np.ndarray = resized_image.astype(np.int16)
    difference = resized - patched
    print(difference.max(), difference.min(), "  \t**", reference_path, patched_path)
    pass


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


def test_patch(original_path: Path, modified_path: Path) -> None:
    patch_path = original_path.with_stem(original_path.stem + "-patch-v6")
    patched_path = original_path.with_stem(original_path.stem + "-patched-v6")
    reversed_path = original_path.with_stem(original_path.stem + "-reversed-v6")
    create_patch(original_path, modified_path, patch_path)
    create_patched(original_path, patch_path, patched_path)
    compare_image(modified_path, patched_path)
    reverse_original(modified_path, patch_path, reversed_path)
    compare_image(original_path, reversed_path)


def test() -> None:
    test_patch(Path("./demo/buzzerfly-icon.png"), Path("./demo/buzzerfly-icon-modified.png"))

if __name__ == "__main__":
    test()