import numpy as np
import typing

from transform import max_luminance


NOISE_VARIANCE = 96
FITLER_NAMES = ["roll-h", "roll-v"] # set
FITLER_NAMES += ["i" + name for name in FITLER_NAMES]


# def max_luminance(x): return 255


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


def moving_average(y, window_width):
    cumsum_vec = np.cumsum(np.insert(y, 0, 0))
    ma_vec = (cumsum_vec[window_width:] - cumsum_vec[:-window_width]) / window_width
    return ma_vec


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def create_noise_array(image: np.ndarray, seed_image: np.ndarray, variance: float, axis: int = 0, relative_variance: bool = True, smooth_pixels: int = 1) -> np.ndarray:
    assert len(image.shape) >= 2
    assert axis in [0, 1]
    np.random.seed(seed=extract_seed(seed_image) % max_luminance(np.dtype(np.uint32)))
    length, max_variance = image.shape[axis - 0], image.shape[1 - axis]
    variance_ = (variance / 100 * max_variance) if relative_variance else variance
    array = np.random.rand(length) * variance_
    if smooth_pixels > 1:
        averages = moving_average(array, smooth_pixels)
        half = smooth_pixels // 2
        array = np.pad(averages, (half, half + 1), "reflect")
    return array.astype(np.int32)


def create_rolled_image(image: np.ndarray, shift: typing.Iterable[int], axis: int = 0) -> np.ndarray:
    assert len(image.shape) >= 2
    copy = image.copy()
    length = image.shape[axis]
    # print(shift[:10])
    for i in range(length):
        idx = [slice(None)] * image.ndim
        idx[axis] = i
        idx = tuple(idx)
        unrolled = image[idx]
        rolled = np.roll(unrolled, (shift[i], *[0 for i in image.shape[2:]]), [i for i in range(len(image.shape[1:]))])
        copy[idx] = rolled
    return copy


def create_bar_inversed_image(image: np.ndarray) -> np.ndarray:
    assert len(image.shape) >= 2
    copy = image.copy()
    for y in range(0, image.shape[0], 2):
        copy[y] = copy[y, ::-1]
    return copy


def channel_inverted(image: np.ndarray) -> np.ndarray:
    pass


def filter_name_to_function(name: str): # callable
    match name:
        case "roll-h":
            def f(image, seed_image):
                shift = create_noise_array(image, seed_image, 10, relative_variance=True, smooth_pixels=40)
                shift -= shift.min()
                filtered = create_rolled_image(image, shift)
                return filtered
            return f
        case "roll-v":
            def f(image, seed_image):
                shift = create_noise_array(image, seed_image, 5, relative_variance=True, smooth_pixels=13, axis=1)
                shift -= shift.min()
                filtered = create_rolled_image(image, shift, axis=1)
                return filtered
            return f
        case "iroll-h":
            def f(image, seed_image):
                shift = create_noise_array(image, seed_image, 10, relative_variance=True, smooth_pixels=40)
                shift -= shift.min()
                filtered = create_rolled_image(image, -shift)
                return filtered
            return f
        case "iroll-v":
            def f(image, seed_image):
                shift = create_noise_array(image, seed_image, 5, relative_variance=True, smooth_pixels=13, axis=1)
                shift -= shift.min()
                filtered = create_rolled_image(image, -shift, axis=1)
                return filtered
            return f
        case _:
            return lambda image: image


def apply_filters(image: np.ndarray, seed_image: np.ndarray, fitler_names: list[str], inverted: bool = False):
    if inverted:
        fitler_names = ["i" + name for name in reversed(fitler_names)]
    assert all([name in FITLER_NAMES for name in fitler_names])
    filtered = image.copy()
    for name in fitler_names:
        filter_function = filter_name_to_function(name)
        filtered = filter_function(filtered, seed_image)
        # print("applying " + name)
    return filtered


def test() -> None:
    """
    >>> s = create_noise_array(im, 10, relative_variance=True, smooth_pixels=20)
    >>> im3 = create_rolled_image(im, s)
    >>> cv2.imshow('image',im3); cv2.waitKey(0); cv2.destroyAllWindows()

    >>> s = create_noise_array(im, 12, relative_variance=True, smooth_pixels=30)
    >>> s -= s.min()
    >>> # cv2.imwrite("./test1.png", im4)
    >>> im4 = create_rolled_image(im, s)
    >>> cv2.imwrite("./test1.png", im4)
    True
    >>> cv2.imwrite("./test4.png", im4)
    True
    >>> cv2.imwrite("./test3.png", im3)

    >>> k = create_noise_array(im, 3, relative_variance=True, smooth_pixels=10, axis=1)
    >>> k[:10]
    array([15, 13, 13, 12, 10,  9, 10, 12, 13, 13])
    >>> k.min()
    8
    >>> k.max()
    33
    >>> k -= k.min()
    >>> im5 = create_rolled_image(im4, k, axis=1)
    """
    pass


if __name__ == "__main__":
    test()