# binary.py
A python library to manipulate binary data.

## Requirements

* Python 3.3+

## Installation

1. [Get the latest version.](https://github.com/neckcen/femto/releases/latest)
2. Unzip it.
3. Run setup.py.

## About binary data

*Disclaimer: this text aims to briefly introduce the concepts behind this
library. It does sacrifice some technical accuracy in favor of pedagogy.*

Computers can only store binary data, zeroes and ones which we call bits. 
However programs often work with more complex data, bigger numbers, text and so 
on. To solve this problem standards were created to code complex structures as
groups of bits. This library lets you read such structures.

The *byte* is the basic structure, it consists of 8 bits and can therefore
represent a maximum of 256 different states (2^8). With binary.py reading a byte
would look like this:

    import binary

    with binary.File('/path/to/file') as binary_file:
        # returns a number between -128 and 127
        binary_file.read_byte()

Since not everything can be reduced to such a small number, there are other 
structures which encompass multiple bytes to store more information. For example
a *short* has a size of *2 bytes* and can represent 65536 different states 
(2^16). At this point we encounter another issue: which byte should be read 
first? This order is called endianness, specifically big endian or little 
endian. 
[Which endianness is used, when and why](https://en.wikipedia.org/wiki/Endianness)
is a long story; what is important is that it must be identical for writing and 
reading. With binary.py endianness defaults to big endian and can be set with 
the endian parameter:

    import binary

    with binary.File('/path/to/file', endian=binary.LITTLE_ENDIAN) as binary_file:
        # returns a number between -32768 and 32767
        binary_file.read_short()

## Constants

* `BE`, `BIG_ENDIAN` - Represents big endian decoding.
* `LE`, `LITTLE_ENDIAN` - Represents little endian decoding.

## Classes

### File(file, mode='r', closefd=True, opener=None, endian=BE)

Open `file` and returns a corresponding binary file object.

* `file` - the path to a file or a file descriptor to be wrapped.
* `mode` - the mode in which the file is opened, see
[open()](https://docs.python.org/3/library/functions.html#open). Note that the
file is always opened in binary mode regardless of `b` being set.
* `closefd` - whether to close the file descriptor when the object is closed.
Only used when `file` is a file descriptor.
* `opener` - custom opener to use, see
[open()](https://docs.python.org/3/library/functions.html#open).
* `endian` - endianness to use. Can be changed later through the `endian`
attribute.

#### Examples

    import binary
    
    # basic usage
    with binary.File('/path/to/file') as binary_file:
        binary_file.read_int()


    import binary

    # with different endianness
    with binary.File('/path/to/file', endian=binary.LE) as binary_file:
        binary_file.read_int()
        binary_file.endian = binary.BE
        binary_file.read_int()


    import binary

    # wrapping a file descriptor
    with open('/path/to/file', 'r+b') as file:
        with binary.File(file.fileno(), closefd=False) as binary_file:
            binary_file.read_int()

        # descriptor wasn't closed
        file.read()


### Buffer(initial_bytes=None, endian=BE)

Create a memory buffer containing `initial_bytes`.

* `initial_bytes` - initial content of the buffer.
* `endian` - endianness to use. Can be changed later through the `endian`
attribute.

Buffer objects can be converted to `bytes`.

The Buffer class offers two convenience methods:

 * `from_file` creates a buffer with the entire content of a file.
 * `from_hex` creates a buffer from an hexadecimal string.


#### Examples

    import binary
    
    # basic usage
    with binary.Buffer(b'\x00\x01') as binary_buffer:
        binary_buffer.read_bool()


    import binary

    # convenient creation from file
    with binary.Buffer.from_file('/path/to/file') as binary_buffer:
        binary_buffer.read_int()


    import binary

    # convenient creation from hex
    with binary.Buffer.from_hex('0001') as binary_buffer:
        binary_buffer.read_bool()


    import binary

    # can be converted to bytes
    with binary.Buffer(b'\x00\x01') as binary_buffer:
        # x now contains b'\x00\x01'
        x = bytes(binary_buffer)

### Wrapper(file_like, endian=BE)

Wrap `file_like` object to add binary read/write methods.

* `file_like` - file-like object to wrap. Must have been opened in binary mode 
if applicable. Must support the following methods: `read`, `write`, `tell`, 
`seek`.
* `endian` - endianness to use. Can be changed later through the `endian`
attribute.

All the methods of the original object are exposed by the wrapped object.

Whenever possible, wrapping a file descriptor with `File()` (see example above) 
should be prefered over the use of `Wrapper()`.

#### Examples

    import binary
    
    # basic usage
    with open('/path/to/file') as file:
        wrapped = binary.Wrapper(file)
        wrapped.read_int()


## Read methods

All the methods described here have a `peek_` counterpart which moves the 
pointer back after reading the value. For example `peek_int()` and `read_int()`. 

### numbers

function name | structue         | size (bytes) | python type
-------------------------------------------------------------
read_bool     | boolean          | 1            | boolean   
read_byte     | byte             | 1            | int
read_ubyte    | unsigned byte    | 1            | int 
read_short    | short            | 2            | int
read_ushort   | unsigned short   | 2            | int 
read_int      | integer          | 4            | int
read_uint     | unsigned integer | 4            | int 
read_long     | long             | 8            | int
read_ulong    | unsigned long    | 8            | int
read_float    | float            | 4            | float
read_double   | double           | 8            | float

### read_hex(length)

Read `length` bytes and return them as an hexadecimal string.

### read_text(length, encoding='utf-8', error='ignore')

Read `length` bytes and decode them using `encoding`.

* `length` - the amount of bytes to read. Beware that some encodings use more 
than one byte per character.
* `encoding` - encoding in which the text is stored.
* `error` - 
[see bytes.decode()](https://docs.python.org/3/library/stdtypes.html#bytes.decode)

The text is truncated at the first nullbyte after decoding.


## Write methods

### Numbers

Values outside of the authorised range or of the wrong type will raise 
`struct.error`.

`write_float` and `write_double` accept the same values but the second store 
them more accurately at the expense of a larger size.

function name | python type | range
-----------------------------------------------
write_bool    | boolean     |      
write_byte    | int         | -128 to 127
write_ubyte   | int         | 0 to 255
write_short   | int         | -32768 to 32767
write_ushort  | int         | 0 to 65535
write_int     | int         | -(2³¹) to 2³¹ - 1
write_uint    | int         | 0 to 2³² - 1
write_long    | int         | -(2⁶³) to 2⁶³ - 1
write_ulong   | int         | 0 to 2⁶⁴ - 1
write_float   | float       |
write_double  | float       |

### write_hex(data, length=None)

Writes the bytes represented by the hexadecimal string `data`. Optional argument
`length` specifies maximum amount of bytes to write.

### write_text(data, encoding='utf-8', length=None)

Writes the text `data` using `encoding`. Optional argument `length` specifies
maximum amount of bytes to write. Beware that some encoding use more than one
byte per character.

## Credits

Binary.py is developed by Sylvain Didelot.

It is merely a friendly interface to the
[struct python module](https://docs.python.org/3/library/struct.html)
which does all the hard work. Part of this documentation comes from the official
python documentation.
