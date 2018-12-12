import struct

CHUNK_TYPE_HEADER = b'MThd'
CHUNK_TYPE_TRACK = b'MTrk'

def read8bit(f):
    return struct.unpack('>B', f.read(1))[0]

def read16bit(f):
    return struct.unpack('>H', f.read(2))[0]

def read32bit(f):
    return struct.unpack('>I', f.read(4))[0]

def readvarint(f):
    result = 0
    for i in range(5):
        byte = read8bit(f)
        result += ((byte & 0x7F) << 7*i)
        if not(byte & 0x80 == 0x80):
            break
    return result, i+1

def read_header(f):
    chunk_type = f.read(4)
    chunk_length = read32bit(f)
    assert chunk_type == CHUNK_TYPE_HEADER
    assert chunk_length == 6
    form = read16bit(f)
    tracks = read16bit(f)
    division = f.read(2)
    return form, tracks, division

def read_meta(f):
    length = 0
    bytes_read = 0
    event_type = f.read(1)
    print('EVENT TYPE', hex(ord(event_type)))
    if event_type == b'\x01':
        length, bytes_read = readvarint(f)
        txt = f.read(length)
        print('TXT', txt)
    if event_type == b'\x03':
        length, bytes_read = readvarint(f)
        txt = f.read(length)
        print('TRACK NAME', txt)
    if event_type == b'\x51':
        tempo = f.read(4)
        print('TEMPO', tempo)
        bytes_read = 4
    if event_type == b'\x2f':
        f.read(1)
        print('TRACK END')
        bytes_read = 1
    return 1+length+bytes_read

def read_sysex(f):
    length, bytes_read = readvarint(f)
    se = f.read(length)
    r = length+bytes_read
    print('SKIP SYSEX BYTES', r, se.hex())
    return r

def read_track(f):
    chunk_type = f.read(4)
    chunk_length = read32bit(f)
    assert chunk_type == CHUNK_TYPE_TRACK
    print(chunk_length)
    bytes_left = chunk_length
    while bytes_left != 0:
        event_time, bytes_read = readvarint(f)
        print('EVENT_TIME', event_time)
        bytes_left -= bytes_read
        event = f.read(1)
        print('EVENT', hex(ord(event)))
        if event == b'\xFF':
            bytes_read = read_meta(f)
        elif event == b'\xF0':
            bytes_read = read_sysex(f)
        else:
            break
        bytes_left -= (1+bytes_read)
    f.read(bytes_left)

path = 'Uriah_Heep_Lady_In_Black.mid'
with open(path, 'rb') as f:
    form, tracks, division = read_header(f)
    for _ in range(tracks):
        read_track(f)
    # do stuff 
