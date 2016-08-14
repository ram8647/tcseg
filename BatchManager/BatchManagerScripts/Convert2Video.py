import PIL
from PIL import Image
import os, os.path, subprocess
from fnmatch import fnmatch
from ModelIOManager import IOManager

def convert_pngs_to_vid(io_manager):
    '''
    module converts images in the screenshot_output_path into a movie
    :type io_manager: IOManger
    '''
    screenshot_parent_dir = io_manager.screenshot_output_path
    png_prefix = os.path.basename(screenshot_parent_dir).split('_')[0]

    # Go through all the subfolders in the screenshot dir, where each folder represents a run...
    for run_dir in os.listdir(screenshot_parent_dir):
        # ...resize the images, if necessary
        if os.path.isdir(os.path.join(screenshot_parent_dir, run_dir)):
            for screenshot_fname in os.listdir(os.path.join(screenshot_parent_dir, run_dir)):
                if fnmatch(name=screenshot_fname, pat='*.png'):
                    # resize images so that the height is dividable by two
                    img_dir = os.path.join(screenshot_parent_dir, run_dir, screenshot_fname)
                    raw_image = Image.open(img_dir)

                    w = raw_image.size[0]
                    if not w % 2 == 0:
                        w = raw_image.size[0] + 1
                    h = raw_image.size[1]
                    if not h % 2 == 0:
                        h = raw_image.size[1] + 1

                    resized_img = raw_image.resize((w, h), PIL.Image.ANTIALIAS)
                    resized_img.save(img_dir)

            # ...then run ffmpeg on them to convert them from a series of images into a .mov
            batch_index = os.path.basename(run_dir)
            png_prefix = png_prefix
            new_working_dir = os.path.join(screenshot_parent_dir, run_dir)
            new_working_dir = new_working_dir.replace(' ','\ ')
            cmd = 'cd {}; ffmpeg -i {}_batch_{}_%02d00.png -framerate 1 -start_number 01 -pix_fmt yuv420p batch_run_{}.mov'.format(
                new_working_dir, png_prefix, batch_index, batch_index)
            try:
                shell_output = subprocess.check_output(cmd, shell=True)
                print(shell_output)
            except:
                raise NameError('Failed to create movie!')