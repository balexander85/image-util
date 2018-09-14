from asyncio import ensure_future, gather, get_event_loop
from datetime import datetime
from logging import basicConfig, captureWarnings, getLogger, INFO
from os import listdir, path, rename
from sys import argv, stdout
from typing import Generator

from PIL import Image


captureWarnings(True)
basicConfig(
    level=INFO,
    format='%(levelname)7s: %(message)s',
    stream=stdout,
)

LOG = getLogger('')


def format_timestamp(timestamp) -> str:
    """Format timestamp to be a file name friendly timestamp"""
    new_fmt = '%Y-%m-%d-%H-%M-%S'
    original_fmt = '%Y:%m:%d %H:%M:%S'
    return datetime.strptime(timestamp, original_fmt).strftime(new_fmt)


def get_image_timestamp(image_file) -> str:
    """Return timestamp from the exif data from image_file"""
    with Image.open(image_file) as img:
        return img._getexif()[36867]


def rename_image(source, destination, skip_dupes=False):
    """Using os.rename method to update image filename to timestamp format"""
    if not path.isfile(destination):
        LOG.info(f"{source} --> {destination}")
        # uncomment when for sure ready to run
        # rename(source, destination)
    elif skip_dupes:
        LOG.info(
            f'SKIPPING - Some sort of duplicate {source} **** {destination}'
        )
    else:
        LOG.info(f'Some sort of duplicate {source} **** {destination}')
        rename(source, destination.replace('.JPG', '-duplicate.JPG'))


def get_list_of_images(photo_dir) -> Generator:
    """Returns a list of images for the given directory

    Note: There is no verification that the files are images however
    .DS_Store files are filtered out.
    """
    for img in listdir(photo_dir):
        if path.isfile(path.join(photo_dir, img)) and img not in ['.DS_Store']:
            yield img


async def process_image(directory_path, image):
    """Take file name and path to process image"""
    img_file_path = path.join(directory_path, image)
    file_ext = image.split('.')[1]
    img_timestamp = get_image_timestamp(img_file_path)
    new_file_name = f'{format_timestamp(img_timestamp)}.{file_ext}'
    new_file_path = path.join(PHOTO_DIRECTORY, new_file_name)
    rename_image(img_file_path, new_file_path)


if __name__ == '__main__':
    start_time = datetime.now()
    home_directory = ''
    try:
        PHOTO_DIRECTORY = f'{home_directory}/Desktop/{argv[1]}'
    except IndexError as e:
        raise Exception('No command line arg passed')

    loop = get_event_loop()
    tasks = [
        ensure_future(process_image(PHOTO_DIRECTORY, img_file))
        for img_file in get_list_of_images(PHOTO_DIRECTORY)
        if path.isfile(path.join(PHOTO_DIRECTORY, img_file))
    ]
    loop.run_until_complete(gather(*tasks, return_exceptions=True))

    duration = datetime.now() - start_time
    LOG.info(f'Total Time: {duration}')
