import re


def get_format_string(link: str):
    """Find the quality, x and y coordinates in the link,
    and replace them by {} placeholders. Returns None if the link does not
    match the right format.
    """
    pat = r'/\d+/\d+/\d+\.png$'
    validate_link(link)
    repl = '/{}/{}/{}.png'
    formatted = re.sub(pat, repl, link)
    return formatted


def validate_link(link: str):
    """Validate format of the supplied link, checking for http[s] and correct
    ending with the required coordinates.
    """
    val_pat = r'https?\S+/\d+/\d+/\d+\.png$'
    if re.search(val_pat, link) is None:
        raise ValueError("The supplied link does not seem valid.")


def max_coordinates(quality: int):
    """Get maximum coordinates for a given map quality.
    Returns a (x, y) tuple
    """
    max_size = 2 ** quality
    return max_size, max_size


def format_link(link: str, quality, x, y):
    """
    """
    return link.format(quality, x, y)

# rm me
if __name__ == '__main__':
    # print(get_format_string("http://b.tiles.telegeography.com/maps/submarine"
    #                         "-cable-map-2016/6/21/47.png"))
    # print(get_format_string("asdjfhbljashdgflajhsdgf"))
