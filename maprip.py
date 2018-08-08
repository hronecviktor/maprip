import time
import glob
import logging
from multiprocessing.dummy import Pool
import os
import re
import shutil
import sys

from PIL import Image
from requests import get

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_tile_spec(base_url: str):
    base_source = get(base_url).text
    jsonp_declaration_re = re.compile(r'http.*\.jsonp')
    matches = jsonp_declaration_re.findall(base_source)
    for match in matches:
        if not str(match).strip().startswith('//'):
            return get(str(match)).text
    else:
        return None


def get_tile_template(base_url: str):
    jsonp_spec = get_tile_spec(base_url=base_url)
    if not jsonp_spec:
        return None

    tile_template_re = re.compile(r'https://.*\{z\}/\{x\}/\{y\}.*\.(?:png|jpg|jpeg)\w+')
    matches = tile_template_re.findall(jsonp_spec)
    if not matches:
        return None

    return str(matches[0])


def check_quality_available(tile_template: str, qual: int):
    logging.debug(f'Checking if quality {qual} is available @ {tile_template.format(z=qual, x=1, y=1)}...')
    response = get(tile_template.format(z=qual, x=1, y=1))
    return response.status_code == 200


def get_max_quality(tile_template: str):
    # Quality of 1 is stupidly low and usually not available
    qual, x, y = 2, 1, 1
    while True:
        if not check_quality_available(tile_template=tile_template, qual=qual):
            return qual -1
        qual += 1


def get_coordinate_bounds(qual: int):
    max_size = 2 ** qual
    return max_size, max_size


def get_tile(url: str):
    filepath_re = re.compile(r'\d+/\d+/\d+\.png')
    path_fragments = filepath_re.findall(url)
    file_path = path_fragments[0]
    file_path = 'tmp_' + file_path.replace('/', '_')
    logging.info(f'Downloading tile {url} to ./{file_path}')
    with open(file_path, 'wb') as fh:
        shutil.copyfileobj(get(url, stream=True).raw, fh)


def download_all_tiles(tile_template: str, qual: int, max_x: int, max_y: int):
    proc_pool = Pool(16)
    urls = [tile_template.format(z=qual, x=x, y=y)
            for x in range(max_x) for y in range(max_y)]
    proc_pool.map(get_tile, urls)
    proc_pool.close()
    proc_pool.join()
    logging.debug(f'Urls to get: {urls}')


def stitch_tiles(qual:int, max_x: int, max_y: int):
    path_template = 'tmp_' + str(qual) + '_{x}_{y}.png'
    image_size = max_x * 256
    final_image = Image.new('RGB', (image_size, image_size))
    for x in range(max_x):
        for y in range(max_y):
            tile = Image.open(path_template.format(x=x, y=y))
            final_image.paste(im=tile, box=(x*256, y*256))
    output_filename = f'{time.time()}.png'
    final_image.save(output_filename)
    logging.info(f'Full map saved to {output_filename} in '
                 f'{image_size}x{image_size}')



def delete_tiles():
    filenames = glob.glob('tmp_*.png')
    for filename in filenames:
        os.remove(filename)


def get_map(base_url: str):
    tile_template = get_tile_template(base_url=base_url)
    logging.debug(tile_template)
    max_quality = get_max_quality(tile_template=tile_template)
    logging.info(f'Maximum quality is {max_quality}')
    max_x, max_y = get_coordinate_bounds(qual=max_quality)
    logging.info(f'Downloading {max_x * max_y} map tiles...')
    download_all_tiles(tile_template=tile_template, qual=max_quality,
                       max_x=max_x, max_y=max_y)
    stitch_tiles(qual=max_quality, max_x=max_x, max_y=max_y)
    delete_tiles()


if __name__ == '__main__':
    url = sys.argv[1]
    get_map(base_url=url)
