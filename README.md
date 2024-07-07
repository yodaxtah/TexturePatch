# TexturePatch

TexturePatch is currently a proof-of-concept tool to create patches to a texture. Many old games have low quality textures, and by hand or by A.I. these can often get upscaled for use in emulators for that console. The problem is however that these textures are copy righted. People that possess a game and are able to extract the textures can enhance them, but they can't share them, as that would be in violation to that copy right.

## Concept

The idea of this tool is to share the updating values, not the original or final values. Let's say a gray-scale image looks like this, where $0$ represents black and $10$ represents white:

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

Features (shape) from the original image are not immediately present, but generally speaking, they are not random either. It can be said that with this approach much more information on the original image is hidden than uploading the manually upscaled image itself.

## Technical aspects

We've made quite a few over simplifications.

1. The difference of two 8-bit images can only be faithfully stored using 9-bit (0-255, 255-0), whereas the patch itself will be an 8 bit image. The tool adds sign descriptors at the bottom of the image and stores the absolute difference.
1. The original image could be reverse engineered if the modified version is published as well. For this reason, additional noise is added to an image. To add the patch to the original image (i.e. create the modified image), the noise will be removed automagically. No keys have to be shared around, they are extracted from the images individually.
1. A chess pattern could be used to swap/shift pixels using the key to further make it more difficult to reverse the original image. Simple pattern swaps (i.e. chess board) will already make it hard for most people, but are also easy to revert with scripting knowledge.

## Q & A

1. _Can't someone publish these keys and a modification of a reversing algorithm to extract the original iamges that requires just the patch and the modified textures?_ Sure, but in any case, they can just as well upload the original or modified textures, which is much less of a hassle.
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

