import pytest


@pytest.fixture
def filename():
    return 'filename0'


@pytest.fixture
def line_number():
    return 42


def test_get_path(path_hash, filename, line_number):
    assert path_hash.get_path(filename, line_number) == '0:42'


def test_append(path_hash, filename, line_number):
    path_hash.get_path(filename, line_number)
    assert path_hash.append(filename, line_number) == '0:42->0:42'


def test_encode(path_hash, filename, line_number):
    assert path_hash._encode(filename, line_number) == '0:42'


def test_decode(path_hash, filename, line_number):
    assert path_hash._decode(path_hash._encode(filename, line_number)) == (filename, line_number)


def test_get_indent(path_hash, filename, line_number):
    assert path_hash.get_indent('') == 0
    assert path_hash.get_indent('0:42') == 1
    assert path_hash.get_indent('0:42->0:42') == 2


def test_get_last_fn_ln(path_hash, filename, line_number):
    assert path_hash.get_last_fn_ln(path_hash._encode(filename, line_number)) == (filename, line_number)


def test_get_code(path_hash, stack_line, filename, line_number):
    path = path_hash.get_stacklines_path([stack_line], 0)
    assert path_hash.get_code(path) == stack_line.code.code


def test_get_stacklines_path(path_hash, stack_line, stack_line_2, filename, line_number):
    assert path_hash.get_stacklines_path([stack_line, stack_line_2], 0) == '1:0'
    assert path_hash.get_stacklines_path([stack_line, stack_line_2], 1) == '1:0->1:0'
