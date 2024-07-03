import cv2
import math
import numpy as np


def resized_to_shape(image: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    # height = shape[0] / image.shape[0]
    # width = shape[1] / image.shape[1]
    # resized_shape = (width, height)
    height, width, number_of_channels = shape
    return cv2.resize(image[:,:,:number_of_channels], (width, height), interpolation=cv2.INTER_CUBIC)


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