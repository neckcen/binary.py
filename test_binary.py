# -*- coding: utf-8 -*-

import pytest

import binascii
import math
import os
import struct
import tempfile

import binary

test_data = b'\x00'*10 + b'\xFF'*5

def temp():
    temp = tempfile.mkstemp(prefix='binary.py')
    os.write(temp[0], test_data)
    os.lseek(temp[0], 0, os.SEEK_SET)
    return temp

@pytest.yield_fixture()
def temp_file():
    descriptor, name = temp()
    os.close(descriptor)
    yield name
    os.remove(name)

@pytest.yield_fixture()
def temp_descriptor():
    descriptor, name = temp()
    yield descriptor
    os.close(descriptor)
    os.remove(name)

class TestBasics:
    """
        Test the basics (creating objects, misc methods).
    """
    def test_create_file(self, temp_file):
        with binary.File(temp_file) as f:
            assert f.read() == test_data

    def test_create_file_from_descriptor(self, temp_descriptor):
        with binary.File(temp_descriptor, closefd=False) as f:
            assert f.read() == test_data

        os.write(temp_descriptor, test_data) #descriptor should not be closed

    def test_create_buffer(self):
        with binary.Buffer(test_data) as b:
            assert b.read() == test_data

    def test_buffer_as_bytes(self):
        with binary.Buffer(test_data) as b:
            assert bytes(b) == test_data

    def test_create_buffer_from_file(self, temp_file):
        with binary.Buffer.from_file(temp_file) as b:
            assert b.read() == test_data

    def test_create_buffer_from_hex(self):
        hex = binascii.hexlify(test_data).decode()
        with binary.Buffer.from_hex(hex) as b:
            assert b.read() == test_data

    def test_create_wrapper(self, temp_file):
        with open(temp_file, 'rb') as f:
            w = binary.Wrapper(f)
            assert w.read() == test_data

    def test_endian(self, temp_file):
        assert binary.BE == binary.BE
        assert binary.LE == binary.LE

        with binary.File(temp_file) as f:
            assert f.endian == binary.BE

        with binary.File(temp_file, endian=binary.BE) as f:
            assert f.endian == binary.BE

        with binary.File(temp_file, endian=binary.LE) as f:
            assert f.endian == binary.LE

    def test_peek(self):
        with binary.Buffer(test_data) as b:
            assert b.peek(len(test_data)) == test_data
            assert b.tell() == 0

    def test_fill(self, temp_file):
        with binary.Buffer() as b:
            b.fill(10)
            b.fill(5, b'\xFF')
            b.seek(0)
            assert b.read() == test_data


class TestPeekRead:
    """
        Check all peek_*/read_* methods return the expected value. Tests are
        performed using Buffer() for convenience as all classes inherit
        _Binary().
    """
    def test_bool(self):
        data = b'\x00\x01\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_bool() == False
            assert b.read_bool() == False
            assert b.peek_bool() == True
            assert b.read_bool() == True
            assert b.peek_bool() == True
            assert b.read_bool() == True

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_bool() == False
            assert b.read_bool() == False
            assert b.peek_bool() == True
            assert b.read_bool() == True
            assert b.peek_bool() == True
            assert b.read_bool() == True

    def test_byte(self):
        data = b'\x00\x01\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_byte() == 0
            assert b.read_byte() == 0
            assert b.peek_byte() == 1
            assert b.read_byte() == 1
            assert b.peek_byte() == -1
            assert b.read_byte() == -1

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_byte() == 0
            assert b.read_byte() == 0
            assert b.peek_byte() == 1
            assert b.read_byte() == 1
            assert b.peek_byte() == -1
            assert b.read_byte() == -1

    def test_ubyte(self):
        data = b'\x00\x01\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_ubyte() == 0
            assert b.read_ubyte() == 0
            assert b.peek_ubyte() == 1
            assert b.read_ubyte() == 1
            assert b.peek_ubyte() == 255
            assert b.read_ubyte() == 255

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_ubyte() == 0
            assert b.read_ubyte() == 0
            assert b.peek_ubyte() == 1
            assert b.read_ubyte() == 1
            assert b.peek_ubyte() == 255
            assert b.read_ubyte() == 255

    def test_short(self):
        data = b'\x00\x00' + b'\x00\x01' + b'\x01\x00' + b'\xFF\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_short() == 0
            assert b.read_short() == 0
            assert b.peek_short() == 1
            assert b.read_short() == 1
            assert b.peek_short() == 256
            assert b.read_short() == 256
            assert b.peek_short() == -1
            assert b.read_short() == -1

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_short() == 0
            assert b.read_short() == 0
            assert b.peek_short() == 256
            assert b.read_short() == 256
            assert b.peek_short() == 1
            assert b.read_short() == 1
            assert b.peek_short() == -1
            assert b.read_short() == -1

    def test_ushort(self):
        data = b'\x00\x00' + b'\x00\x01' + b'\x01\x00' + b'\xFF\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_ushort() == 0
            assert b.read_ushort() == 0
            assert b.peek_ushort() == 1
            assert b.read_ushort() == 1
            assert b.peek_ushort() == 256
            assert b.read_ushort() == 256
            assert b.peek_ushort() == 65535
            assert b.read_ushort() == 65535

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_ushort() == 0
            assert b.read_ushort() == 0
            assert b.peek_ushort() == 256
            assert b.read_ushort() == 256
            assert b.peek_ushort() == 1
            assert b.read_ushort() == 1
            assert b.peek_ushort() == 65535
            assert b.read_ushort() == 65535

    def test_int(self):
        data = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00' + b'\xFF\xFF\xFF\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_int() == 0
            assert b.read_int() == 0
            assert b.peek_int() == 1
            assert b.read_int() == 1
            assert b.peek_int() == 65536
            assert b.read_int() == 65536
            assert b.peek_int() == -1
            assert b.read_int() == -1

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_int() == 0
            assert b.read_int() == 0
            assert b.peek_int() == 16777216
            assert b.read_int() == 16777216
            assert b.peek_int() == 256
            assert b.read_int() == 256
            assert b.peek_int() == -1
            assert b.read_int() == -1

    def test_uint(self):
        data = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00' + b'\xFF\xFF\xFF\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_uint() == 0
            assert b.read_uint() == 0
            assert b.peek_uint() == 1
            assert b.read_uint() == 1
            assert b.peek_uint() == 65536
            assert b.read_uint() == 65536
            assert b.peek_uint() == 4294967295
            assert b.read_uint() == 4294967295

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_uint() == 0
            assert b.read_uint() == 0
            assert b.peek_uint() == 16777216
            assert b.read_uint() == 16777216
            assert b.peek_uint() == 256
            assert b.read_uint() == 256
            assert b.peek_uint() == 4294967295
            assert b.read_uint() == 4294967295

    def test_float(self):
        data = b'\x00\x00\x00\x00' + b'\x3F\x80\x00\x00' + b'\x7F\xC0\x00\x00'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_float() == 0.
            assert b.read_float() == 0.
            assert b.peek_float() == 1.
            assert b.read_float() == 1.
            assert math.isnan(b.peek_float()) == True
            assert math.isnan(b.read_float()) == True

        data = b'\x00\x00\x00\x00' + b'\x00\x00\x80\x3F' + b'\x00\x00\xC0\x7F'

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_float() == 0.
            assert b.read_float() == 0.
            assert b.peek_float() == 1.
            assert b.read_float() == 1.
            assert math.isnan(b.peek_float()) == True
            assert math.isnan(b.read_float()) == True

    def test_long(self):
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x00\x00\x00\x00\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00\x00\x00\x00\x00' + \
            b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_long() == 0
            assert b.read_long() == 0
            assert b.peek_long() == 1
            assert b.read_long() == 1
            assert b.peek_long() == 281474976710656
            assert b.read_long() == 281474976710656
            assert b.peek_long() == -1
            assert b.read_long() == -1

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_long() == 0
            assert b.read_long() == 0
            assert b.peek_long() == 72057594037927936
            assert b.read_long() == 72057594037927936
            assert b.peek_long() == 256
            assert b.read_long() == 256
            assert b.peek_long() == -1
            assert b.read_long() == -1

    def test_ulong(self):
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x00\x00\x00\x00\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00\x00\x00\x00\x00' + \
            b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_ulong() == 0
            assert b.read_ulong() == 0
            assert b.peek_ulong() == 1
            assert b.read_ulong() == 1
            assert b.peek_ulong() == 281474976710656
            assert b.read_ulong() == 281474976710656
            assert b.peek_ulong() == 18446744073709551615
            assert b.read_ulong() == 18446744073709551615

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_ulong() == 0
            assert b.read_ulong() == 0
            assert b.peek_ulong() == 72057594037927936
            assert b.read_ulong() == 72057594037927936
            assert b.peek_ulong() == 256
            assert b.read_ulong() == 256
            assert b.peek_ulong() == 18446744073709551615
            assert b.read_ulong() == 18446744073709551615

    def test_double(self):
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x3F\xF0\x00\x00\x00\x00\x00\x00' + \
            b'\x7F\xF8\x00\x00\x00\x00\x00\x00'

        with binary.Buffer(data, endian=binary.BE) as b:
            assert b.peek_double() == 0.
            assert b.read_double() == 0.
            assert b.peek_double() == 1.
            assert b.read_double() == 1.
            assert math.isnan(b.peek_double()) == True
            assert math.isnan(b.read_double()) == True

        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x00\x00\x00\x00\x00\x00\xF0\x3F' + \
            b'\x00\x00\x00\x00\x00\x00\xF8\x7F'

        with binary.Buffer(data, endian=binary.LE) as b:
            assert b.peek_double() == 0.
            assert b.read_double() == 0.
            assert b.peek_double() == 1.
            assert b.read_double() == 1.
            assert math.isnan(b.peek_double()) == True
            assert math.isnan(b.read_double()) == True

    def test_hex(self):
        data = b'\x00\x01\xFF'
        hex = '0001ff'

        with binary.Buffer(data) as b:
            assert b.peek_hex(3) == hex
            assert b.read_hex(3) == hex

    def test_text(self):
        data = b'\xC3\xA8\x2E\xC3\xA9' + b'\xC3\xA8\x2E\xC3\xA9' + \
            b'\xC3\xA8\x2E\xC3\xA9\x00\xC3\xA8\x2E\xC3\xA9' + \
            b'\xE8\x2E\xE9' + b'\xC3\xA8\x2E\xC3\xA9'
        text = 'è.é'

        with binary.Buffer(data) as b:
            assert b.peek_text(5) == text
            assert b.read_text(5) == text
            assert b.peek_text(5, encoding='utf-8') == text
            assert b.read_text(5, encoding='utf-8') == text
            assert b.peek_text(11) == text
            assert b.read_text(11) == text
            assert b.peek_text(3, encoding='iso-8859-1') == text
            assert b.read_text(3, encoding='iso-8859-1') == text
            with pytest.raises(UnicodeDecodeError):
                b.peek_text(5, encoding='utf-16be', error='strict')
            with pytest.raises(UnicodeDecodeError):
                b.read_text(5, encoding='utf-16be', error='strict')

class TestWrite:
    """
        Check all write_* methods produce the expected value. Tests are performed
        using Buffer() for convenience as all classes inherit _Binary().
    """
    def test_bool(self):
        data = b'\x01\x00'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_bool(True)
            b.write_bool(False)
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_bool(True)
            b.write_bool(False)
            assert bytes(b) == data

    def test_byte(self):
        data = b'\x00\x01\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_byte(0)
            b.write_byte(1)
            b.write_byte(-1)
            with pytest.raises(struct.error):
                b.write_byte(128)
            with pytest.raises(struct.error):
                b.write_byte('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_byte(0)
            b.write_byte(1)
            b.write_byte(-1)
            assert bytes(b) == data

    def test_ubyte(self):
        data = b'\x00\x01\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_ubyte(0)
            b.write_ubyte(1)
            b.write_ubyte(255)
            with pytest.raises(struct.error):
                b.write_ubyte(-1)
            with pytest.raises(struct.error):
                b.write_ubyte('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_ubyte(0)
            b.write_ubyte(1)
            b.write_ubyte(255)
            assert bytes(b) == data

    def test_short(self):
        data = b'\x00\x00' + b'\x00\x01' + b'\x01\x00' + b'\xFF\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_short(0)
            b.write_short(1)
            b.write_short(256)
            b.write_short(-1)
            with pytest.raises(struct.error):
                b.write_short(32768)
            with pytest.raises(struct.error):
                b.write_short('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_short(0)
            b.write_short(256)
            b.write_short(1)
            b.write_short(-1)
            assert bytes(b) == data

    def test_ushort(self):
        data = b'\x00\x00' + b'\x00\x01' + b'\x01\x00' + b'\xFF\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_ushort(0)
            b.write_ushort(1)
            b.write_ushort(256)
            b.write_ushort(65535)
            with pytest.raises(struct.error):
                b.write_ushort(-1)
            with pytest.raises(struct.error):
                b.write_ushort('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_ushort(0)
            b.write_ushort(256)
            b.write_ushort(1)
            b.write_ushort(65535)
            assert bytes(b) == data

    def test_int(self):
        data = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00' + b'\xFF\xFF\xFF\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_int(0)
            b.write_int(1)
            b.write_int(65536)
            b.write_int(-1)
            with pytest.raises(struct.error):
                b.write_int(2147483648)
            with pytest.raises(struct.error):
                b.write_int('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_int(0)
            b.write_int(16777216)
            b.write_int(256)
            b.write_int(-1)
            assert bytes(b) == data

    def test_uint(self):
        data = b'\x00\x00\x00\x00' + b'\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00' + b'\xFF\xFF\xFF\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_uint(0)
            b.write_uint(1)
            b.write_uint(65536)
            b.write_uint(4294967295)
            with pytest.raises(struct.error):
                b.write_uint(-1)
            with pytest.raises(struct.error):
                b.write_uint('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_uint(0)
            b.write_uint(16777216)
            b.write_uint(256)
            b.write_uint(4294967295)
            assert bytes(b) == data

    def test_float(self):
        data = b'\x00\x00\x00\x00' + b'\x3F\x80\x00\x00' + b'\x7F\xC0\x00\x00'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_float(0.)
            b.write_float(1.)
            b.write_float(float('NaN'))
            with pytest.raises(struct.error):
                b.write_float('a')
            assert bytes(b) == data

        data = b'\x00\x00\x00\x00' + b'\x00\x00\x80\x3F' + b'\x00\x00\xC0\x7F'

        with binary.Buffer(endian=binary.LE) as b:
            b.write_float(0.)
            b.write_float(1.)
            b.write_float(float('NaN'))
            assert bytes(b) == data

    def test_long(self):
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x00\x00\x00\x00\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00\x00\x00\x00\x00' + \
            b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_long(0)
            b.write_long(1)
            b.write_long(281474976710656)
            b.write_long(-1)
            with pytest.raises(struct.error):
                b.write_long(9223372036854775808)
            with pytest.raises(struct.error):
                b.write_long('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_long(0)
            b.write_long(72057594037927936)
            b.write_long(256)
            b.write_long(-1)
            assert bytes(b) == data

    def test_ulong(self):
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x00\x00\x00\x00\x00\x00\x00\x01' + \
            b'\x00\x01\x00\x00\x00\x00\x00\x00' + \
            b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_ulong(0)
            b.write_ulong(1)
            b.write_ulong(281474976710656)
            b.write_ulong(18446744073709551615)
            with pytest.raises(struct.error):
                b.write_ulong(-1)
            with pytest.raises(struct.error):
                b.write_ulong('a')
            assert bytes(b) == data

        with binary.Buffer(endian=binary.LE) as b:
            b.write_ulong(0)
            b.write_ulong(72057594037927936)
            b.write_ulong(256)
            b.write_ulong(18446744073709551615)
            assert bytes(b) == data

    def test_double(self):
        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x3F\xF0\x00\x00\x00\x00\x00\x00' + \
            b'\x7F\xF8\x00\x00\x00\x00\x00\x00'

        with binary.Buffer(endian=binary.BE) as b:
            b.write_double(0.)
            b.write_double(1.)
            b.write_double(float('NaN'))
            assert bytes(b) == data

        data = b'\x00\x00\x00\x00\x00\x00\x00\x00' + \
            b'\x00\x00\x00\x00\x00\x00\xF0\x3F' + \
            b'\x00\x00\x00\x00\x00\x00\xF8\x7F'

        with binary.Buffer(endian=binary.LE) as b:
            b.write_double(0.)
            b.write_double(1.)
            b.write_double(float('NaN'))
            assert bytes(b) == data

    def test_hex(self):
        data = b'\x00\x01\xFF\x00'
        hex = '0001ff'

        with binary.Buffer() as b:
            b.write_hex(hex)
            b.write_hex(hex, length=1)
            assert bytes(b) == data

    def test_text(self):
        data = b'\xC3\xA8\x2E\xC3\xA9' + b'\xC3\xA8\x2E\xC3\xA9' + \
            b'\xE8\x2E\xE9' + b'\xC3\xA8'
        text = 'è.é'

        with binary.Buffer() as b:
            b.write_text(text)
            b.write_text(text, encoding='utf-8')
            b.write_text(text, encoding='iso-8859-1')
            b.write_text(text, length=2)
            assert bytes(b) == data
