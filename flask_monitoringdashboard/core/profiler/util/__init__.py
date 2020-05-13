from flask_monitoringdashboard.core.profiler.util.path_hash import PathHash


def order_histogram(items, path=''):
    """
    Finds the order of self._text_dict and assigns this order to self._lines_body
    :param items: list of key, value. Obtained by histogram.items()
    :param path: used to filter the results
    :return The items, but sorted
    """
    sorted_list = []
    indent = PathHash.get_indent(path) + 1

    order = sorted(
        [
            (key, value)
            for key, value in items
            if key[0][: len(path)] == path and PathHash.get_indent(key[0]) == indent
        ],
        key=lambda row: row[0][1],
    )
    for key, value in order:
        sorted_list.append((key, value))
        sorted_list.extend(order_histogram(items=items, path=key[0]))
    return sorted_list
