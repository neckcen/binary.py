# -*- coding: utf-8 -*-

"""
    binary.py, a python library to easily manipulate binary data.
"""

import binascii
import io
import os
import struct

__version__ = '0.1.0'
__all__ = ['File', 'Buffer', 'Wrapper']

"""
    Improve performances by reusing Struct objects.
"""
BE = BIG_ENDIAN = {
    'symbol': '>',
    'bool': struct.Struct('?'),
    'byte': struct.Struct('b'),
    'ubyte': struct.Struct('B'),
    'short': struct.Struct('>h'),
    'ushort': struct.Struct('>H'),
    'int': struct.Struct('>i'),
    'uint': struct.Struct('>I'),
    'float': struct.Struct('>f'),
    'long': struct.Struct('>q'),
    'ulong': struct.Struct('>Q'),
    'double': struct.Struct('>d'),
}
LE = LITTLE_ENDIAN = {
    'symbol': '<',
    'bool': BIG_ENDIAN['bool'],
    'byte': BIG_ENDIAN['byte'],
    'ubyte': BIG_ENDIAN['ubyte'],
    'short': struct.Struct('<h'),
    'ushort': struct.Struct('<H'),
    'int': struct.Struct('<i'),
    'uint': struct.Struct('<I'),
    'float': struct.Struct('<f'),
    'long': struct.Struct('<q'),
    'ulong': struct.Struct('<Q'),
    'double': struct.Struct('<d'),
}

class _Binary:
    """
        Contain all the code to convert to/from binary.

        Do not contain the actual read() and write() methods and as such is
        not intended for direct use.
    """
    def fill(self, length, value=b'\x00'):
        """
            Fill <length> with optional <value> (defaults: nullbyte).
        """
        self.write(value * length)

    def peek(self, length=-1):
        """
            Read <length> then put the pointer back to where it was and return
            what was read.
        """
        position = self.tell()
        data = self.read(length)
        self.seek(position)
        return data

    def peek_bool(self):
        return self.endian['bool'].unpack(self.peek(1))[0]
    def peek_byte(self):
        return self.endian['byte'].unpack(self.peek(1))[0]
    def peek_ubyte(self):
        return self.endian['ubyte'].unpack(self.peek(1))[0]
    def peek_short(self):
        return self.endian['short'].unpack(self.peek(2))[0]
    def peek_ushort(self):
        return self.endian['ushort'].unpack(self.peek(2))[0]
    def peek_int(self):
        return self.endian['int'].unpack(self.peek(4))[0]
    def peek_uint(self):
        return self.endian['uint'].unpack(self.peek(4))[0]
    def peek_float(self):
        return self.endian['float'].unpack(self.peek(4))[0]
    def peek_long(self):
        return self.endian['long'].unpack(self.peek(8))[0]
    def peek_ulong(self):
        return self.endian['ulong'].unpack(self.peek(8))[0]
    def peek_double(self):
        return self.endian['double'].unpack(self.peek(8))[0]
    def peek_hex(self, length):
        return binascii.hexlify(self.peek(length)).decode()
    def peek_text(self, length, encoding='utf-8', error='ignore'):
        data = self.peek(length).decode(encoding, error)
        # http://mail.python.org/pipermail/tutor/2001-June/006382.html
        try:
            data = data[:data.index('\x00')]
        except ValueError:
            pass
        return data

    def read_bool(self):
        return self.endian['bool'].unpack(self.read(1))[0]
    def read_byte(self):
        return self.endian['byte'].unpack(self.read(1))[0]
    def read_ubyte(self):
        return self.endian['ubyte'].unpack(self.read(1))[0]
    def read_short(self):
        return self.endian['short'].unpack(self.read(2))[0]
    def read_ushort(self):
        return self.endian['ushort'].unpack(self.read(2))[0]
    def read_int(self):
        return self.endian['int'].unpack(self.read(4))[0]
    def read_uint(self):
        return self.endian['uint'].unpack(self.read(4))[0]
    def read_float(self):
        return self.endian['float'].unpack(self.read(4))[0]
    def read_long(self):
        return self.endian['long'].unpack(self.read(8))[0]
    def read_ulong(self):
        return self.endian['ulong'].unpack(self.read(8))[0]
    def read_double(self):
        return self.endian['double'].unpack(self.read(8))[0]
    def read_hex(self, length):
        return binascii.hexlify(self.read(length)).decode()
    def read_text(self, length, encoding='utf-8', error='ignore'):
        data = self.read(length).decode(encoding, error)
        try:
            data = data[:data.index('\x00')]
        except ValueError:
            pass
        return data

    def write_bool(self, data):
        self.write(self.endian['bool'].pack(data))
    def write_byte(self, data):
        self.write(self.endian['byte'].pack(data))
    def write_ubyte(self, data):
        self.write(self.endian['ubyte'].pack(data))
    def write_short(self, data):
        self.write(self.endian['short'].pack(data))
    def write_ushort(self, data):
        self.write(self.endian['ushort'].pack(data))
    def write_int(self, data):
        self.write(self.endian['int'].pack(data))
    def write_uint(self, data):
        self.write(self.endian['uint'].pack(data))
    def write_float(self, data):
        self.write(self.endian['float'].pack(data))
    def write_long(self, data):
        self.write(self.endian['long'].pack(data))
    def write_ulong(self, data):
        self.write(self.endian['ulong'].pack(data))
    def write_double(self, data):
        self.write(self.endian['double'].pack(data))
    def write_hex(self, data, length=None):
        data = binascii.unhexlify(data.encode())
        self.write_length(data, length)
    def write_text(self, data, encoding='utf-8', length=None):
        data = data.encode(encoding)
        self.write_length(data, length)
    def write_length(self, data, length=None):
        if length is not None:
            data = struct.pack('{}{}s'.format(self.endian['symbol'], length), data)
        self.write(data)


class File(io.FileIO, _Binary):
    """
        Open a binary file.

        see also: https://docs.python.org/3/library/io.html#io.FileIO
    """
    def __init__(self, file, mode='r', closefd=True, opener=None, endian=BE):
        self.endian = endian
        super().__init__(file, mode, closefd, opener)


class Buffer(io.BytesIO,_Binary):
    """
        Create a binary buffer in memory.

        see also: https://docs.python.org/3/library/io.html#io.BytesIO
    """
    def __init__(self, initial_bytes=None, endian=BE):
        self.endian = endian
        super().__init__(initial_bytes)

    def __bytes__(self):
        pointer = self.tell()
        self.seek(0)
        b = self.read()
        self.seek(pointer)
        return b

    @classmethod
    def from_file(cls, file, endian=BE):
        """
            Place the entire content of a file in a buffer. Return that
            buffer.
        """
        with open(file, 'rb') as f:
            buf = cls(f.read(), endian)
        return buf

    @classmethod
    def from_hex(cls, hex, endian=BE):
        """
            Decode an hexadecimal string and places its content in a buffer.
            Return that buffer.
        """
        return cls(binascii.unhexlify(hex.encode()), endian)


class Wrapper(_Binary):
    """
        Add binary methods to a file-like object.

        warning: The file-like object must be opened in binary mode if
        applicable.
    """
    def __init__(self, file_like, endian=BE):
        self._file_like = file_like
        self.endian = endian

    def __getattr__(self, attr):
        return getattr(self._file_like, attr)

