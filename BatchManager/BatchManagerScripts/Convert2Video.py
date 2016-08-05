import PIL
from PIL import Image
import os, os.path, subprocess
from fnmatch import fnmatch
from ModelIOManager import IOManager

def convert_pngs_to_vid():
    screenshot_parent_dir = IOManager().screenshot_output_path
    screenshot_dir = None
    project_name = None

    #Find the directory with all the screenshots
    parent_sub_directories = os.listdir(screenshot_parent_dir)
    for dir in parent_sub_directories:
        if fnmatch(dir, '')


    for dir in sub_directories:
        images = (img for img in os.listdir(dir) if fnmatch(name=img, pat='*.png'))
        for img in images:
            # resize images so that the height is dividable by two
            img_dir = os.path.join(dir, img)
            raw_image = Image.open(img_dir)
            if not raw_image.size[1] % 2 == 0:
                w = raw_image.size[0]
                h = raw_image.size[1] + 1
                resized_img = raw_image.resize((w, h), PIL.Image.ANTIALIAS)
                resized_img.save(img_dir)

        batch_index = os.path.basename(dir)
        cmd = 'cd {}; /usr/local/bin/ffmpeg -i {}_{}_%02d00.png -framerate 1 -start_number 01 -pix_fmt yuv420p {}{}.mov'.format(dir, png_prefix, batch_index, 'output_vid_', batch_index)
        try:
            shell_output = subprocess.check_output(cmd, shell=True)
            print(shell_output)
        except:
            print('Failed to create movie. Is ffmpeg installed?')