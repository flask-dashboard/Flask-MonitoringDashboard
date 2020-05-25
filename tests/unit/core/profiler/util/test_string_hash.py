import pytest


def test_stringhash(string_hash):
    assert string_hash.hash('abc') == 0
    assert string_hash.hash('def') == 1
    assert string_hash.hash('abc') == 0


def test_unhash(string_hash):
    assert string_hash.unhash(string_hash.hash('abc')) == 'abc'

    with pytest.raises(ValueError):
        string_hash.unhash('unkown')
