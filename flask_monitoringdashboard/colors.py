from colorhash import ColorHash
from flask_monitoringdashboard import config


def get_color(hash):
    """
    Returns an rgb-color (as string, which can be using in plotly) from a given hash,
    if no color for that string was specified in the config file.
    :param hash: the string that is translated into a color
    :return: a color (as string)
    """
    if hash in config.colors:
        rgb = config.colors[hash]
    else:
        rgb = ColorHash(hash).rgb
    return 'rgb({0}, {1}, {2})'.format(rgb[0], rgb[1], rgb[2])
