import os
import sys
import logging
from datetime import datetime
from typing import Generator

from PIL import Image
# import pytesseract


logging.captureWarnings(True)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)7s: %(message)s",
    stream=sys.stdout,
)

LOG = logging.getLogger("")


def format_timestamp(timestamp) -> str:
    """
        Format timestamp to be a file name friendly timestamp
    """
    new_fmt = "%Y-%m-%d-%H-%M-%S"
    original_fmt = "%Y:%m:%d %H:%M:%S"
    return datetime.strptime(timestamp, original_fmt).strftime(new_fmt)


def get_image_timestamp(image_file) -> str:
    """
        Return timestamp from the exif data from image_file
    """
    with Image.open(image_file) as img:
        return img._getexif()[36867]


def rename_img_file(source, destination, skip_dupes=False):
    if not os.path.isfile(destination):
        LOG.info(f"{source} --> {destination}")
        # uncomment when for sure ready to run
        # os.rename(source, destination)
    elif skip_dupes:
        LOG.info(
            f"SKIPPING - Some sort of duplicate {source} **** {destination}"
        )
    else:
        LOG.info(f"Some sort of duplicate {source} **** {destination}")
        os.rename(source, destination.replace(".JPG", "-duplicate.JPG"))


def get_list_of_images(photo_dir) -> Generator:
    """
        Returns a list of images for the given directory
        Note: There is no verification that the files are images
    """
    for img in os.listdir(photo_dir):
        if os.path.isfile(os.path.join(photo_dir, img)) and img not in (
            '.DS_Store'
        ):
            yield img


if __name__ == "__main__":
    start_time = datetime.now()
    home_directory = ""
    try:
        PHOTO_DIRECTORY = f"{home_directory}/Desktop/{sys.argv[1]}"
    except IndexError as e:
        PHOTO_DIRECTORY = f"{home_directory}~/Desktop/field"

    images_renamed = []

    for img_file in get_list_of_images(PHOTO_DIRECTORY):
        img_file_path = os.path.join(PHOTO_DIRECTORY, img_file)
        file_ext = img_file.split('.')[1]
        if os.path.isfile(img_file_path):
            img_timestamp = get_image_timestamp(img_file_path)
            new_file_name = f"{format_timestamp(img_timestamp)}.{file_ext}"
            new_file_path = os.path.join(PHOTO_DIRECTORY, new_file_name)
            rename_img_file(img_file_path, new_file_path)
            images_renamed.append(img_timestamp)

    duration = datetime.now() - start_time
    LOG.info(f"Total Time: {duration}")
