# Upscaling textures with `process` and `Upscayl`

In case you would like a more in depth tutorial of how you can use this program to help upscaling a bulk of textures, you can follow this guide. We're going to upscale all textures in the `socksky` package of the FOSS game [Cube 2: Sauerbraten](http://sauerbraten.org/) using the FOSS upscaler [Upscayl](https://upscayl.org/download).

## Installing the cli upscaler

> [!NOTE]
> Upscayl already provides a bulk upscale feature. While it runs into a bug after 12-16 images, it might be fixed by the time you are reading this.

> [!WARNING]
> The necessary executeable on Windows retains a path bug, where it mixes both forward and backward slashes. (You will an error similar like this one: `Error: Failed to open C:\Program Files\Upscayl\resources\bin\models/realesrgan-x4plus-anime.param`) I haven't figured out how to fix this, which prevents it from succesfully running an upscaling operation. This tutorial focuses on Linux.

When installing the Upscayl, you will find the underlying cli program and models the application uses at its installation `resources` directory.

- On Windows, the executable will have a path like `C:\Program Files\Upscayl\resources\bin\upscayl-bin.exe`
- On Linux, installed through Flatpak, the executable will have a path like `/var/lib/flatpak/app/org.upscayl.Upscayl/x86_64/stable/12345...abc...xyz/files/upscayl/resources/bin/upscayl-bin`

This is the exact same executable you'll also find in the released binaries of [upscayl-ncnn](https://github.com/upscayl/upscayl-ncnn), but without models.

## Setting up a working directory with `upscayl-bin`

The following is fish code. The only difference with bash would be using the `=` syntax instead of the `set` command. We're going to create a temporary folder to put all our temporary content in.

```bash
set project ~/Projects/Skyboxes
mkdir $project -p
cd $project
```

You might consider downloading or copying the content from system installations over to . The Flatpak app already errors out by default after an image has been generated due to writing permissions.

```bash
# Get the ncnn binary
wget "https://github.com/upscayl/upscayl-ncnn/releases/download/20240601-103425/upscayl-bin-20240601-103425-linux.zip"

# Extract the zip content (which can also happen in gui or with "7z X" if not installed)
unzip upscayl-bin-20240601-103425-linux.zip

# alias the downloaded/copied upscaler to user space
set upsc "$$project/upscayl-bin"

# ALTERNATIVELY TO DOWNLOADING NCNN: you can copy the binary from you Upscayl installation
cp "/var/lib/flatpak/app/org.upscayl.Upscayl/x86_64/stable/6a97b...17bg1/files/upscayl/resources/bin/upscayl-bin" $upsc
```

Now the binary has no models, thus just copy them over. Or link them.

```bash
# symbolically link the models folder in system space
ln -s "/var/lib/flatpak/app/org.upscayl.Upscayl/x86_64/stable/6a97b...17bg1/files/upscayl/resources/models" "$$project/models"
```

## Setting up a source and destination directories

Let's set our source and destination directories for the image pack. We do this for readability, you can also inline them later.

```bash
# set folder where original images reside
set original "/var/lib/flatpak/app/org.sauerbraten.Sauerbraten/current/active/files/share/sauerbraten/packages/socksky"

# set folder where upscaled images will reside
set upscaled "/home/me/.var/app/org.sauerbraten.Sauerbraten/.sauerbraten/packages/socksky" 
```

Alternatively, if you have a dual boot you can also use the Windows paths.

```bash
# set folder where original images reside
set original "/media/me/Windows/Program Files (x86)/Sauerbraten/packages/socksky"

# set folder where upscaled images will reside
set upscaled "/media/me/Windows/Users/me/Documents/My Games/Sauerbraten/packages/socksky"
```

## Verifying our custom command works

Next, we try our custom cli command on 1 image, to check if everything works. We selected `barren_bk.jpg` from the available images in this test.

```bash
# check which images are available
ls $original

# try the upscale command with a large tile size to be quick (128)
$upsc -i $original/barren_bk.jpg -o $upscaled/barren_bk_test.jpg -f jpg -z 4 -c 0 -t 128 -n upscayl-standard-4x

# if that worked out, test a few images with a few parameters from $upsc --help to see what works best.
```

## `process`ing the images

If the previous worked out and you are sure about the selected parameters you're going to pass to the upscaler, you can run it on all images. Beware that this will take a long time, especially if the tile size is small.

```bash
# process each image in $original and place it in $upscaled with the same relative file structure
python main.py process "$upsc -i [:original:] -o [:processed:] -f jpg -z 4 -c 0 -t 32 -n upscayl-standard-4x" $original $upscaled
```

Note that the order appears not always to be alphabetic. (For example, desert_lf.jpg appears much later than the rest of desert's skybox images.) The output should be the following:

```txt
original (66)
  ✔ barren_bk.jpg
  ✔ barren_dn.jpg
  ✔ barren_ft.jpg
  ✔ barren_lf.jpg
  ✔ barren_rt.jpg
  ✔ barren_up.jpg
  ✔ desert_bk.jpg
  ✔ desert_dn.jpg
  ✔ desert_ft.jpg
  ✔ desert_rt.jpg
  ✔ desert_up.jpg
  ✔ devpun_bk.jpg
  ✔ devpun_dn.jpg
  ✔ devpun_ft.jpg
  ✔ devpun_lf.jpg
  ✔ devpun_rt.jpg
  ✔ devpun_up.jpg
  ✔ emerald_bk.jpg
  ✔ emerald_dn.jpg
  ✔ emerald_ft.jpg
  ✔ emerald_lf.jpg
  ✔ emerald_rt.jpg
  ✔ emerald_up.jpg
  ✔ frozendusk_bk.jpg
  ✔ frozendusk_dn.jpg
  ✔ frozendusk_ft.jpg
  ✔ frozendusk_lf.jpg
  ✔ frozendusk_rt.jpg
  ✔ frozendusk_up.jpg
  ✔ frozen_bk.jpg
  ✔ frozen_dn.jpg
  ✔ frozen_ft.jpg
  ✔ frozen_lf.jpg
  ✔ frozen_rt.jpg
  ✔ frozen_up.jpg
  ✔ grave_bk.jpg
  ✔ grave_ft.jpg
  ✔ grave_lf.jpg
  ✔ grave_rt.jpg
  ✔ grave_up.jpg
  ✔ mars_bk.jpg
  ✔ mars_dn.jpg
  ✔ mars_ft.jpg
  ✔ mars_lf.jpg
  ✔ mars_rt.jpg
  ✔ mars_up.jpg
  ✔ nightball_bk.jpg
  ✔ nightball_dn.jpg
  ✔ nightball_ft.jpg
  ✔ nightball_lf.jpg
  ✔ nightball_rt.jpg
  ✔ desert_lf.jpg
  ✔ grave_dn.jpg
  ✔ nightball_up.jpg
  ✔ stratosphere_bk.jpg
  ✔ stratosphere_dn.jpg
  ✔ stratosphere_ft.jpg
  ✔ stratosphere_lf.jpg
  ✔ stratosphere_rt.jpg
  ✔ stratosphere_up.jpg
  ✔ valley_bk.jpg
  ✔ valley_dn.jpg
  ✔ valley_ft.jpg
  ✔ valley_lf.jpg
  ✔ valley_rt.jpg
  ✔ valley_up.jpg
```