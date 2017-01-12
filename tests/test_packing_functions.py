from cachual import (pack_json, unpack_json, unpack_int, unpack_long,
                     unpack_float, unpack_bool, unpack_json_python3)

import sys
if (sys.version_info > (3, 0)):
    def unicode(value):
        return str(value)

    def long(value):
        return int(value)

from mock import MagicMock, mock

import pytest, sys

@mock.patch("cachual.json")
def test_pack_json(mock_json):
    test_value = "testing"
    mock_json.dumps = MagicMock(return_value=test_value)
    
    assert pack_json("test") == test_value
    mock_json.dumps.assert_called_with("test")

@mock.patch("cachual.json")
def test_unpack_json(mock_json):
    test_value = "testing"
    mock_json.loads = MagicMock(return_value=test_value)

    assert unpack_json("test") == test_value
    mock_json.loads.assert_called_with("test")

def test_unpack_json_python3():
    if (sys.version_info > (3, 0)):
        test_value = bytes('{"test": "testing"}', encoding="utf-8")
    else:
        test_value = str('{"test": "testing"}')
    assert unpack_json_python3(test_value) == {"test": "testing"}

def test_unpack_int():
    test_value = "3"
    assert unpack_int(test_value) == int(test_value)

def test_unpack_long():
    test_value = "3"
    assert unpack_long(test_value) == long(test_value)

def test_unpack_float():
    test_value = "3.2"
    assert unpack_float(test_value) == float(test_value)

def test_unpack_bool_true():
    test_value = 'True'
    assert unpack_bool(test_value) == True

def test_unpack_bool_false():
    test_value = 'False'
    assert unpack_bool(test_value) == False

def test_unpack_bool_invalid():
    test_value = 'Invalid'
    with pytest.raises(ValueError):
        unpack_bool(test_value)
