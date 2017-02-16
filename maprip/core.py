import shutil as sh
from multiprocessing.dummy import Pool

import requests as req
from helpers import *

# TODO: Create temporary directory somewhere, delete it afterwards


TEMP_TEMPLATE = "/tmp/maprip/{}-{}-{}.png"


def get_max_quality(link: str, max_qual: int = 22):
    """
    """
    min_qual = 2
    coords = 0, 0
    link = get_format_string(link)
    for qual in range(min_qual, max_qual + 1):
        tile_addr = format_link(link, qual, *coords)
        # TODO: debug
        print("requesting {}".format(qual))
        resp = req.get(tile_addr)
        if resp.status_code != 200:
            if qual <= 2:
                raise RuntimeError("Could not reach even the minimum quality "
                                   "tile at {}, HTTP {}".format(tile_addr,
                                                            resp.status_code))
            break
    qual -= 1
    return qual


def _get_tile(args):
    link, qual, x, y = args
    # TODO: debug
    print("Downloading img {}x{} out of {}x{}".format(x, y, *max_coordinates(
        qual)))
    resp = req.get(format_link(*args), stream=True)
    with open(TEMP_TEMPLATE.format(qual, x, y), 'wb') as fh:
        sh.copyfileobj(resp.raw, fh)


def download_pieces(link, qual, num_processes = 16):
    ppool = Pool(num_processes)
    max_size, _ = max_coordinates(qual)
    data = ([(link, qual, x, y)
            for x in range(max_size)
            for y in range(max_size)])
    ppool.map(_get_tile, data)
    ppool.close()
    ppool.join()


if __name__ == '__main__':
    # l = "http://b.tiles.telegeography.com/maps/submarine-cable-map-20" \
    #     "16/6/21/47.png"
    # print(get_max_quality(l))
    # # get_tile(("http://b.tiles.telegeography.com/maps/submarine-cable"
    # #                  "-map-2016/{}/{}/{}.png", 6, 1, 2))
    # _link = get_format_string(l)
    # download_pieces(_link, 4, 32)
