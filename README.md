# TexturePatch

TexturePatch is currently a proof-of-concept tool to create patches to a texture. Many old games have low quality textures, and by hand or by A.I. these can often get upscaled for use in emulators for that console. The problem is however that these textures are copy righted. People that possess a game and are able to extract the textures can enhance them, but they can't share them, as that would be in violation to that copy right.

## Concept

The idea of this tool is to share the updating values, not the original or final values of an image. Let's say a gray-scale image looks like this, where $0$ represents black and $10$ represents white:

$$
Original = \begin{bmatrix}
1   & 4   & 6   \\
3   & 5   & 7   \\
4   & 2   & 8    
\end{bmatrix}
$$

And someone increased its saturation as follows:

$$
Modified = \begin{bmatrix}
0   & 4   & 6   \\
2   & 5   & 8   \\
4   & 1   & 10    
\end{bmatrix}
$$

What this tool will do (heavily simplified) is calculate its difference, and store it in a new image.

$$
Patch = Modified - Original = \begin{bmatrix}
-1  & 0   & 0   \\
-1  & 0   & 1   \\
0   & -1  & 2    
\end{bmatrix}
$$

We've made quite a few over simplifications.

1. Image dimensions may vary (i.e. $25\times25$ for the original and $300\times300$ for the modified one). In order to create a difference, the sizes should be the same. The only option really is to resize the original image to the new dimension with a standard method. (The tools uses cubic interpolation because the result is better and computation takes _longer_.)
1. The difference of two 8-bit images can only be faithfully stored using 9-bit $(0-255, 255-0)$, whereas the patch itself will be an 8 bit image. The tool adds sign descriptors at the bottom of the image and stores the absolute difference.

## Protecting the original image from reversing

Given that the formula in the concept is only a difference, one could simply calculate $Reversed = Patch - Modified = Original$ without ever needing the original. Similarly, when $Original$ is already to be found somewhere publically, one wouldn't be able to publish $Patch$, because it will also open the door to reversing the original. This is quite inpractical, especially since a few modified images had already been published. To address this limitation, a protected formula is used, seen below.

$$
Patch = Modified - Original + Noise(Seed(Original))
$$
$$
Reversed = Modified - Patch + Noise(0) \neq Original
$$

To correctly reverse the image, it is now necessary to have the original image (or just the seed), making the point of reversing the image pointless. The noise will have sufficiently high variance (currently 96) so that the reversed luminances will be too hard to correct, and the texture will be unusable as a texture. Moreover, the size information of the original texture is not added to the patch. This approach has the advantage that no key has to be shared around to share patches, they are extracted from the images individually.

Again, simplifications are made. Now, the range is no longer 9 bit (to maximally represent $(-256, 255)$), since the noise can overflow it. With $(0,n)$ being the range for the noise, the total patch range would become $(0-255+0, 255-0+n)$. Additional data will have to be stored. The lazy solution was to just add the occassions where the noise was inverted. This will be visible as the other row of mini textures.

Patterns could be used to swap/shift pixels that require the seed to make reversing even more difficult. In fact, simple pattern swaps (i.e. rotating pixels on black tiles of the chess board) that don't require the seed will already make it hard for most people to do something practically with the patch or a reversed image, but these patterns are also easy to revert with scripting knowledge, since the algorithm can be inspected.

## Usage

The script can only be executed with python installed. It requires both open cv and numpy to be added to a default installation.

Help can be found for each command running `main.py --help` and `main.py create --help` and so on. Below, we'll give example commands for [crate-brown-wood.jpg](./demo/crate-brown-wood.jpg). (Be careful, paths in the example have png and jpg extensions!)

### `create`

Running the following command will create a patch texture in [./demo/crate-brown-wood-patch.png](./demo/crate-brown-wood-patch.png) given the paths to the original and modified textures. This method currently also works recursively on directories.

```console
python main.py create ./demo/crate-brown-wood.jpg ./demo/crate-brown-wood-modified.png ./demo/crate-brown-wood-patch.png
```

### `apply`

Running the following command will apply the patch to the original texture in [./demo/crate-brown-wood-patch.png](./demo/crate-brown-wood-patch.png). This method currently also works recursively on directories.

```console
python main.py apply ./demo/crate-brown-wood.jpg ./demo/crate-brown-wood-patch.png ./demo/crate-brown-wood-patched.png
```

### `diff`

As a patch creator, one can ensure it matches exactly by running the following command, which will print `(min, max)` ~~_only if there is a difference_~~. The following command compares the modified and patched images, which will (should!) have 0 difference, and thus will not print anything.

```console
python main.py diff ./demo/crate-brown-wood-modified.png ./demo/crate-brown-wood-patched.png # may only prints if there is a difference!
```

Adding a third path will always generate a difference image, in which white represents little change, blue represents luminance decrease and red represents luminance increase. Since this is a view on 3 channels, all channels (R, G, B) had been added up for comparison. The following command will additionally create a difference image at [./demo/crate-brown-wood-patch-{firstname}-{secondname}.png](./demo/crate-brown-wood-difference-modified-patched-crate-brown-wood-modified-crate-brown-wood-patched.png). The naming behavior will change in the future.

```console
python main.py diff ./demo/crate-brown-wood-modified.png ./demo/crate-brown-wood-patched.png ./demo/crate-brown-wood-difference-modified-patched.png
```

### `reverse`

Finally, to see if the noise is large enough, the following command will create a reversed image at [./demo/crate-brown-wood-reversed.png](./demo/crate-brown-wood-patch.png) with using 0 for each noise value -- since the original is presumed not to be accessible and thus unknown.

```console
python main.py reverse ./demo/crate-brown-wood-modified.png ./demo/crate-brown-wood-patch.png ./demo/crate-brown-wood-reversed.png
```

You can pass in the this image to `diff` to compare the differences with the "original" modified image.

### `test`

To run all these commands for just two images, the following command will create all these textures at the location of the modified texture.

```console
python main.py test ./demo/crate-brown-wood.jpg ./demo/crate-brown-wood-modified.png
```

It would be the equivalent of running (although some names will get a version number for now).

```console
python main.py create  ./demo/crate-brown-wood.jpg          ./demo/crate-brown-wood-modified.png ./demo/crate-brown-wood-patch.png
python main.py apply   ./demo/crate-brown-wood.jpg          ./demo/crate-brown-wood-patch.png    ./demo/crate-brown-wood-patched.png
python main.py diff    ./demo/crate-brown-wood-modified.png ./demo/crate-brown-wood-patched.png  ./demo/crate-brown-wood-difference-modified-patched.png
python main.py reverse ./demo/crate-brown-wood-modified.png ./demo/crate-brown-wood-patch.png    ./demo/crate-brown-wood-reversed.png
python main.py diff    ./demo/crate-brown-wood-reversed.png ./demo/crate-brown-wood-patched.png  ./demo/crate-brown-wood-difference-reversed-patched.png
```

## Demo

Conceptually speaking, the difference between two similar images should be small, and size of the image should also be smaller. Of course, heavy noise is added, which goes against image compression algorithms. Besides that point, these small differences tend to give away the edges present in a texture -- the overal shape. This is currently a consideration to make when using the tool. On the other hand, the colors can't be reversed, nor the size of the orignal image. Someone that does not have access to the original textures is time-wise better of obtaining them somewhere online illegally, than doing manual cleaning of the edges. (Attempts are welcome to see the effectiveness!)

### crate-brown-wood.jpg

We took a publically avaiable $512\times512$ texture for a wooden crate from [opengameart.org](https://opengameart.org/content/box-and-barrel-textures-crate-brown-wood.jpg). This image had been shamelessly upscaled using the FOSS [Upscayl](https://github.com/upscayl/upscayl) application to a $2560\times2560$ image. All textures this tool generates can be found in [demo](./demo/).

- [original crate-brown-wood in jpg](./demo/crate-brown-wood.jpg)
- [modified crate-brown-wood in png](./demo/crate-brown-wood-modified.png)
- [patch for crate-brown-wood in png](./demo/crate-brown-wood-patch.png)
- [patched crate-brown-wood in png](./demo/crate-brown-wood-patched.png)
- [reversed crate-brown-wood in png](./demo/crate-brown-wood-reversed.png)
- [difference for modified and patched crate-brown-wood in png](./demo/crate-brown-wood-difference-modified-patched-crate-brown-wood-modified-crate-brown-wood-patched.png)
- [difference for modified and reversed crate-brown-wood in png](./demo/crate-brown-wood-difference-reversed-patched-crate-brown-wood-reversed-crate-brown-wood-patched.png)

Notice that the original is a jpg, but the modified is a png. This is why the modified texture can still be faithfully recreated with the patch, unlike the next texture, which has a modified jpg texture.

### CF_DSC05592.jpg

We took a publically availabe $720\times480$ image from [duion.com](https://duion.com/art/photos/cfdsc05592jpg) to test modified jpgs and upscaled with Upscayl to $4320\times2880$. Notice that the patch should still be a png to preserve as much information as possible, but even though it gets faithfully recreated, the data will be written and small changes invisible to the eye will occur -- this image will print out `(-19, 19)` for the difference between patched and modified.

Notice that the original is a jpg, but the modified is not, whereas before, the original was a png and the modified as a png.

- [original duion-art-photos-CF_DSC05592 in jpg](./demo/duion-art-photos-CF_DSC05592.jpg)
- [modified duion-art-photos-CF_DSC05592 in jpg](./demo/duion-art-photos-CF_DSC05592-modified.jpg)
- [patch for duion-art-photos-CF_DSC05592 in png](./demo/duion-art-photos-CF_DSC05592-patch.png)
- [patched duion-art-photos-CF_DSC05592 in jpg](./demo/duion-art-photos-CF_DSC05592-patched.jpg)
- [reversed duion-art-photos-CF_DSC05592 in jpg](./demo/duion-art-photos-CF_DSC05592-reversed.jpg)
- [difference for modified and patched duion-art-photos-CF_DSC05592 in jpg](./demo/duion-art-photos-CF_DSC05592-difference-modified-patched-duion-art-photos-CF_DSC05592-modified-duion-art-photos-CF_DSC05592-patched.jpg)
- [difference for modified and reversed duion-art-photos-CF_DSC05592 in jpg](./demo/duion-art-photos-CF_DSC05592-difference-reversed-patched-duion-art-photos-CF_DSC05592-reversed-duion-art-photos-CF_DSC05592-patched.jpg)

<!-- Features (shape) from the original image are not immediately present, but generally speaking, they are not random either. It can be said that with this approach much more information on the original image is hidden than uploading the manually upscaled image itself.

It is clearly not just a random image. The patch in itself will contain some information on the texture. This can be obfuscated visually, but it will be there either way in some form. -->

## Q & A

1. _Can't someone publish these keys and a modification of a reversing algorithm to extract the original images that requires just the patch and the modified textures?_ Sure, but in any case, they can just as well upload the original or modified textures, which is much less of a hassle.
1. _Are 16-bit png images are supported?_ Yes, but no. The patching works, but it is not yet meant to be used. The original image has to be scaled (**which is currently not the case!**), otherwise, there will be very little difference visible (0-255) compared to (0-65535), and the patch can be just downsampled, creating a very good attempt at reversing the original.
1. _Are jpgs supported?_ JPGs are a lossy format (that I personally wouldn't expect for games), thus to create a patch for them that results in the exact same jpg is unlikely. The tool creates a png patch, but upon storing the eventual patched image as jpg, some of the data gets lost. This would/should be the case as well when reading and directly writing the image -- yet to be tried. These differences are hardly visible to the eye.
1. _What are these iccp warnings?_ I'm not sure exactly ([some corruption of the modified image](https://stackoverflow.com/questions/22745076/libpng-warning-iccp-known-incorrect-srgb-profile)), but the goal is to exactly recreate the image. If the modified image is corrupted before patched, then the eventual patched image will have it too.
1. _What needs to be done?_
    - All textures from Dash 's pack have been patched without immediate error (a few images in the replacement pack exist that are not present in the decompiled images). Further testing is necessary to find more bugs before the tool is actually used. The format of the patch could change after all, which would become annoying when a patch uses the old format.
    - Platform specific quirks should be tested, so that the result is the same.
    - Decent CLI should be provided.
    - Perhaps store the patch(ed) image with a different library. [Open CV appears to increase the size of the image](https://stackoverflow.com/questions/12216333/opencv-imread-imwrite-increases-the-size-of-png), even though the luminances are exactly the same.
1. _Is this method safe?_ For now, I'd say yes. However, I strongly suspect this hashing is not quantum computing safe "only" $2^{32}-1$ keys exist, so for each image, one could just try them all at once with a quantum computer and determine which match the best with the modified image using an algorithm. But then again, it takes quite a lot of effort. This should only be a concern for the game company that could be publishing patches, or allows artists to publish patches on publically unavailable textures. But that in itself is already extremely unlikely! All the other people that have the goal of finding the original textures waste much less time searching for them online, sadly.
<!-- . When that time comes, the textures should be taken offline. It still extra work to reverse a patch and a modified version to the original image, but it is certainly possible. At the same time. I don't expect anyone to put in the effort to reverse textures, if they can be found somewhere. The only unsafe use case is when this were to be used by a company that allowed artists to work on the original textures and publish them as patches. Anyone else will just grab them somewhere -- it is way too time consuming to reverse this! -->

