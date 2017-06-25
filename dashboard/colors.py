from colorhash import ColorHash


def get_color(hash):
    """
    Returns an rgb-color (as string, which can be using in plotly) from a given hash
    :param hash: the string that is translated into a color
    :return: a color (as string)
    """
    c = ColorHash(hash)
    rgb = c.rgb
    return 'rgb({0}, {1}, {2})'.format(rgb[0], rgb[1], rgb[2])

