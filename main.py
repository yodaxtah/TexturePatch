import numpy as np
import cv2


def create_noise_image(original_image: np.ndarray, variance: float = 20) -> np.ndarray:
    assert variance in range(0,256)
    height, width = original_image.shape
    minimum = original_image.min()
    maximum = original_image.max()
    summation = original_image.sum()
    seed = width * height * (maximum - minimum) + summation
    np.random.seed(seed=seed)
    noise = np.random.rand(height, width) * 100
    return noise.astype(np.uint8)


def create_patch():
    resized_image = cv2.imread('./buzzerfly-icon-resized.png', cv2.IMREAD_UNCHANGED)
    modified_image = cv2.imread('./buzzerfly-icon-modified.png', cv2.IMREAD_UNCHANGED)

    resized: np.ndarray = resized_image.astype(np.int16)
    modified: np.ndarray = modified_image.astype(np.int16)
    difference: np.ndarray = modified - resized
    is_positive: np.ndarray = difference >= 0

    difference_image: np.ndarray = np.absolute(difference).astype(np.uint8)
    cv2.imwrite("./buzzerfly-icon-patch.png", difference_image)

    np.save("./buzzerfly-icon-patch-signs.npy", is_positive)


def create_patched():
    resized_image = cv2.imread('./buzzerfly-icon-resized.png', cv2.IMREAD_UNCHANGED).astype(np.int16)
    difference_image = cv2.imread("./buzzerfly-icon-patch.png", cv2.IMREAD_UNCHANGED).astype(np.int16)
    is_positive_data = np.load("./buzzerfly-icon-patch-signs.npy").astype(np.bool_)

    is_positive: np.ndarray = is_positive_data
    resized: np.ndarray = resized_image.astype(np.int16)
    difference: np.ndarray = np.invert(is_positive) * -difference_image + is_positive * difference_image
    modified: np.ndarray = difference + resized

    modified_image = modified.astype(np.uint8)
    cv2.imwrite("./buzzerfly-icon-patched.png", modified_image)


def to_absolute_ordered(elements: list[int], ascending: bool = True) -> list[int]:
    key = (lambda x: abs(x)) if ascending else (lambda x: -abs(x))
    return sorted(elements, key=key)


def calculate_top_differences(number_of_differences: int = 10) -> list[int]:
    modified_image = cv2.imread('./buzzerfly-icon-patched.png', cv2.IMREAD_UNCHANGED).astype(np.int16)
    patched_image = cv2.imread('./buzzerfly-icon-patched.png', cv2.IMREAD_UNCHANGED).astype(np.int16)

    modified: np.ndarray = modified_image.astype(np.int16)
    patched: np.ndarray = patched_image.astype(np.int16)
    difference: np.ndarray = modified - patched
    
    difference_values = difference.flatten('K').tolist()
    sorted_values = to_absolute_ordered(difference_values, ascending=False)
    top_values = sorted_values[:number_of_differences]
    print(top_values)
    # return top_values


create_patch()
create_patched()
calculate_top_differences()