# Compressing images with PNG Crush

The `process` command is also useful for end users that wish to further compress the images without dataloss, given that [Open CV appears to increase the size of the image](https://stackoverflow.com/questions/12216333/opencv-imread-imwrite-increases-the-size-of-png). Below, we demonstrate that an image loaded and written unmodified gets a larger file size.

```python
>>> import cv2
>>> image = cv2.imread("./demo/logo.png", cv2.IMREAD_UNCHANGED) # 1.16 MB
>>> cv2.imwrite("./demo/logo-written.png", image) # suddenly 1.31 MB
True
```

Several compression tools exist for lossless (or lossy) compression, some even have python wrapped libraries. Some tools have a higher compression ratio at the expense of time, some prioritize time more. However, some players might not even want to waste this additional time on files that will look the same anyway. For this reason, we leave it up to the player to decide what additional tools should be run on the images. Below are a few tools, in no particular order, some of which are lossy.

- [pngcrush](https://pmt.sourceforge.io/pngcrush/)
- [pngcrunch](https://github.com/the-real-neil/pngcrunch/)
- [optipng](https://optipng.sourceforge.net/)
- [kenutils](https://www.jonof.id.au/kenutils.html)
- [crunch](https://github.com/chrissimpkins/Crunch)
- [zopfli](https://github.com/google/zopfli)
- [fpng](https://github.com/richgel999/fpng)
- [pngquant](https://github.com/kornelski/pngquant)

We provide an example for `pngcrush`, but generally, to know where to put the placeholders, just execute your-compressor, and the first line will usually tell you where "input" or "input image" is expected and "output". For `pngcrush`, the basic command looks like `pngcrush original.png processed.png`. We can execute this using our tool, or we can investigate the `--help` command / look online for the best results according to your needs, which may be prioritizing the smallest size.

```console
# default options for pngcrush
python main.py process "pngcrush [:original:] [:processed:]" ./demo/logo.png ./demo/logo.png-compressed-default
# options for pngcrush to run all 114 algorithms and pick best result (much slower!!)
python main.py process "pngcrush  -rem allb -brute -reduce [:original:] [:processed:]" ./demo/logo.png ./demo/logo.png-compressed-brute`
```

With the [default options](./demo/logo-compressed-default.png), our logo was compressed in 17s to size 1.13MB. With the [brute force method](./demo/logo-compressed-brute.png), it took 2m54s to only reduce it 1KB more (which is not worth the time and CPU wear). This doesn't mean of course that therefore other tools are only competing over a few bytes. [Zopfli should have an additional reduction of 6% to gzip](https://www.telerik.com/blogs/maximize-compression-with-zopfli) while pngcrush uses gzip, although no exe was readily available to test it out.