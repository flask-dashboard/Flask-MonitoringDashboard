from flask import render_template

from flask_monitoringdashboard import blueprint
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.utils import get_endpoint_details
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.execution_path_line import get_grouped_profiled_requests

OUTLIERS_PER_PAGE = 10
SEPARATOR = ' / '


def get_body(index, lines):
    """
    Return the lines (as a list) that belong to the line given in the index
    :param index: integer, between 0 and length(lines)
    :param lines: all lines belonging to a certain request. Every element in this list is an ExecutionPathLine-obj.
    :return: an empty list if the index doesn't belong to a function. If the list is not empty, it denotes the body of
    the given line (by the index).
    """
    body = []
    indent = lines[index].get('indent')
    index += 1
    while index < len(lines) and lines[index].get('indent') > indent:
        body.append(index)
        index += 1
    return body


def get_path(lines, index):
    """
    Returns a list that corresponds to the path to the root.
    For example, if lines consists of the following code:
    0.  f():
    1.      g():
    2.          time.sleep(1)
    3.      time.sleep(1)
    get_path(lines, 0) ==> ['f():']
    get_path(lines, 3) ==> ['f():', 'time.sleep(1)']
    :param lines: List of ExecutionPathLine-objects
    :param index: integer in range 0 .. len(lines)
    :return: A list with strings
    """
    path = []
    while index >= 0:
        path.append(lines[index].line_text)
        current_indent = lines[index].indent
        while index >= 0 and lines[index].indent != current_indent - 1:
            index -= 1
    return SEPARATOR.join(reversed(path))


def has_prefix(path, prefix):
    """
    :param path: execution path line
    :param prefix
    :return: True, if the path contains the prefix
    """
    if prefix is None:
        return True
    return path.startswith(prefix)


def sort_equal_level_paths(paths):
    """
        :param paths: List of tuples (ExecutionPathLines, [hits])
        :return: list sorted based on the total number of hits
        """
    return sorted(paths, key=lambda tup: sum(tup[1]), reverse=True)


def sort_lines(lines, partial_list, level=1, prefix=None):
    """
    Returns the list of execution path lines, in the order they are supposed to be printed.
    As input, it will get something like: [def endpoint():_/_g()_/_f(), def endpoint():_/_g()_/_f()_/_time.sleep(1),
    def endpoint():_/_g(), @app.route('/endpoint'), def endpoint():_/_f()_/_time.sleep(1), def endpoint():,
    def endpoint():_/_f()]. The sorted list should be:
    [@app.route('/endpoint'), def endpoint():, def endpoint():_/_time.sleep(0.001), def endpoint():_/_f(),
    def endpoint():_/_f()_/_time.sleep(1), def endpoint():_/_g(), def endpoint():_/_g()_/_f(),
    def endpoint():_/_g()_/_f()_/_time.sleep(1)]

    :param lines: List of tuples (ExecutionPathLines, [hits])
    :param partial_list: the final list at different moments of computation
    :param level: the tree depth. level 1 means root
    :param prefix: this represents the parent node in the tree
    :return: List of sorted tuples
    """
    equal_level_paths = []
    for l in lines:
        if len(l[0].split(SEPARATOR)) == level:
            equal_level_paths.append(l)

    # if we reached the end of a branch, return
    if len(equal_level_paths) == 0:
        return partial_list

    if level == 1:  # ugly hardcoding to ensure that @app.route stays first
        equal_level_paths = sorted(equal_level_paths, key=lambda tup: tup[0])
    else:  # we want to display branches with most hits first
        equal_level_paths = sort_equal_level_paths(equal_level_paths)

    for l in equal_level_paths:
        if has_prefix(l[0], prefix):
            partial_list.append(l)
            sort_lines(lines, partial_list, level + 1, prefix=l[0])
    return partial_list


@blueprint.route('/endpoint/<end>/grouped-profiler')
@secure
def grouped_profiler(end):
    with session_scope() as db_session:
        details = get_endpoint_details(db_session, end)
        data = get_grouped_profiled_requests(db_session, end)
    total_execution_time = 0
    total_hits = 0
    for d in data:
        total_execution_time += d[0].execution_time
        total_hits += d[1][0].value

    # total hits ........ total execution time ms
    #     x hits ........     y execution time ms
    # y = x * (total exec time / total hits)
    coefficient = total_execution_time/total_hits

    histogram = {}  # path -> [list of values]
    for _, lines in data:
        for index in range(len(lines)):
            key = get_path(lines, index)
            line = lines[index]
            if key in histogram:
                histogram[key].append(line.value)
            else:
                histogram[key] = [line.value]

    unsorted_tuples_list = []
    for k, v in histogram.items():
        unsorted_tuples_list.append((k, v))
    sorted_list = sort_lines(lines=unsorted_tuples_list, partial_list=[], level=1)

    table = []
    index = 0
    for line in sorted_list:
        split_line = line[0].split(SEPARATOR)
        sum_ = sum(line[1])
        count = len(line[1])
        table.append({
            'index': index,
            'indent': len(split_line),
            'code': split_line[-1],
            'hits': len(line[1]),
            'total': sum_ * coefficient,
            'average': sum_ / count * coefficient,
            'percentage': sum_ / total_hits
        })
        index += 1

    return render_template('fmd_dashboard/profiler_grouped.html', details=details, table=table, get_body=get_body,
                           average_time=total_execution_time/len(data),
                           title='Grouped Profiler results for {}'.format(end))
