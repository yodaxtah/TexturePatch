import cv2
import numpy as np


NOISE_VARIANCE = 96


def resized_to_shape(image: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    # height = shape[0] / image.shape[0]
    # width = shape[1] / image.shape[1]
    # resized_shape = (width, height)
    shape = (shape[0], shape[1])
    return cv2.resize(image, shape, interpolation=cv2.INTER_LINEAR)


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


def create_patch(original_path: str, modified_path: str, patch_path: str, noise_path: str, shift_path: str):
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

    patch_image: np.ndarray = shifted.astype(np.uint8)
    cv2.imwrite(patch_path, patch_image)
    np.save(noise_path, np.packbits(difference_is_positive.reshape(-1)))
    np.save(shift_path, np.packbits(hashed_is_positive.reshape(-1)))


def create_patched(original_path: str, patch_path: str, noise_path: str, shift_path: str, patched_path: str):
    patch_image = cv2.imread(patch_path, cv2.IMREAD_UNCHANGED)
    original_image = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
    resized_image = resized_to_shape(original_image, patch_image.shape)
    difference_is_positive = np.unpackbits(np.load(noise_path)).reshape(patch_image.shape).astype(bool)
    hashed_is_positive = np.unpackbits(np.load(shift_path)).reshape(patch_image.shape).astype(bool)

    shifted = patch_image.astype(np.int16)
    hashed = sign_unshifted_image(hashed_is_positive, shifted)

    resized: np.ndarray = resized_image.astype(np.int16)
    noise: np.ndarray = create_noise_image(resized, NOISE_VARIANCE)
    difference = hashed + signed(difference_is_positive, noise)
    patched: np.ndarray = difference + resized

    patched_image: np.ndarray = patched.astype(np.int16)
    cv2.imwrite(patched_path, patched_image)


def compare_image(reference_path: str, patched_path: str) -> None:
    reference_image = cv2.imread(reference_path, cv2.IMREAD_UNCHANGED)
    patched_image = cv2.imread(patched_path, cv2.IMREAD_UNCHANGED)
    resized_image = resized_to_shape(reference_image, patched_image.shape)
    
    patched: np.ndarray = patched_image.astype(np.int16)
    resized: np.ndarray = resized_image.astype(np.int16)
    difference = resized - patched
    print(difference.max(), difference.min(), "  \t**", reference_path, patched_path)
    pass


def reverse_original(modified_path: str, patch_path: str, noise_path: str, shift_path: str, reversed_path: str) -> None:
    modified_image = cv2.imread(modified_path, cv2.IMREAD_UNCHANGED)
    patch_image = cv2.imread(patch_path, cv2.IMREAD_UNCHANGED)
    difference_is_positive = np.unpackbits(np.load(noise_path)).reshape(patch_image.shape).astype(bool)
    hashed_is_positive = np.unpackbits(np.load(shift_path)).reshape(patch_image.shape).astype(bool)

    shifted = patch_image.astype(np.int16)
    hashed = sign_unshifted_image(hashed_is_positive, shifted)
    
    noise: np.ndarray = np.zeros(hashed.shape) # create_noise_image(resized, 0)
    difference = hashed + signed(difference_is_positive, noise)
    modified: np.ndarray = modified_image.astype(np.int16)
    resized = modified - difference
    reversed_image: np.ndarray = resized.astype(np.uint8)
    cv2.imwrite(reversed_path, reversed_image)


def test() -> None:
    original_path = "./buzzerfly/buzzerfly-icon.png"
    modified_path = "./buzzerfly/buzzerfly-icon-modified.png"
    patch_path = "./buzzerfly-icon-patch-v5.png"
    noise_path = "./buzzerfly-icon-patch-noise.npy"
    shift_path = "./buzzerfly-icon-patch-shift.npy"
    patched_path = "./buzzerfly-icon-patched-v5.png"
    reversed_path = "./buzzerfly-icon-reversed-v5.png"
    create_patch(original_path, modified_path, patch_path, noise_path, shift_path)
    create_patched(original_path, patch_path, noise_path, shift_path, patched_path)
    compare_image(modified_path, patched_path)
    reverse_original(modified_path, patch_path, noise_path, shift_path, reversed_path)
    compare_image(original_path, reversed_path)
    pass


if __name__ == "__main__":
    test()