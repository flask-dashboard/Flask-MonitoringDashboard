from flask_monitoringdashboard.core.profiler.util.pathHash import PathHash, LINE_SPLIT


def order_histogram(items, path='', with_code=False):
    """
    Finds the order of self._text_dict and assigns this order to self._lines_body
    :param items: list of key, value. Obtained by histogram.items()
    :param path: used to filter the results
    :param with_code: if true, the path is encoded as a tuple of 3 elements, otherwise 2 elements
    :return: The items, but sorted
    """
    sorted_list = []
    indent = PathHash.get_indent(path) + 1

    if with_code:
        order = sorted([(key, value) for key, value in items
                        if key[:len(path)] == path and PathHash.get_indent(key) == indent],
                       key=lambda row: row[0].split(LINE_SPLIT, 2)[2])
    else:
        order = sorted([(key, value) for key, value in items
                        if key[0][:len(path)] == path and PathHash.get_indent(key[0]) == indent],
                       key=lambda row: row[0][1])
    for key, value in order:
        sorted_list.append((key, value))
        path = key if with_code else key[0]
        sorted_list.extend(order_histogram(items=items, path=path, with_code=with_code))
    return sorted_list
