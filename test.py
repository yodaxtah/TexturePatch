from patch import create_patch, create_patched
from difference import compare_image, reverse_original

import numpy as np
from pathlib import Path


def test_patch(original_path: Path, modified_path: Path) -> None:
    patch_path = modified_path.with_stem(original_path.stem + "-patch-v8-1").with_suffix(".png") # must be lossless
    patched_path = modified_path.with_stem(original_path.stem + "-patched-v8-1").with_suffix(modified_path.suffix)
    reversed_path = modified_path.with_stem(original_path.stem + "-reversed-v8-1").with_suffix(modified_path.suffix)
    difference_path = modified_path.with_stem(original_path.stem + "-difference-v8-1").with_suffix(modified_path.suffix)
    create_patch(original_path, modified_path, patch_path)
    create_patched(original_path, patch_path, patched_path)
    if (difference := compare_image(modified_path, patched_path, difference_path)) != (0, 0):
        print("patched difference:", difference)
    reverse_original(modified_path, patch_path, reversed_path)
    compare_image(original_path, reversed_path, difference_path)
    if (difference := compare_image(original_path, reversed_path, difference_path)) != (0, 0):
        print("reverse difference:", difference)


def test() -> None:
    destination = Path("./test/image")
    test_patch(destination.joinpath("./hud-powercell.png"), destination.joinpath("./hud-powercell-modified.png"))
    test_patch(destination.joinpath("./assis-choker.png"), destination.joinpath("./assis-choker-modified.png"))
    test_patch(destination.joinpath("./dc-handle-02.png"), destination.joinpath("./dc-handle-02-modified.png"))
    test_patch(destination.joinpath("./buzzerfly-icon.png"), destination.joinpath("./buzzerfly-icon-modified.png"))
    test_patch(destination.joinpath("./crate-brown-wood.jpg"), destination.joinpath("./crate-brown-wood-modified.png"))
    test_patch(destination.joinpath("./duion-art-photos-CF_DSC05592.jpg"), destination.joinpath("./duion-art-photos-CF_DSC05592-modified.jpg"))

if __name__ == "__main__":
    test()