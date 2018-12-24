import struct
import io
import collections

CHUNK_TYPE_HEADER = b'MThd'
CHUNK_TYPE_TRACK = b'MTrk'

class DivisionFormat(Exception):
    pass
class EventUnknown(Exception):
    pass

class MidiEvent():
    NOTE_ON = 0
    NOTE_OFF = 1
    CONTROLLER_CHANGE = 2
    PROGRAM_CHANGE = 3
    PITCH_BENDER = 4
    _data_size = {
        NOTE_ON: 2,
        NOTE_OFF: 2,
        CONTROLLER_CHANGE: 2,
        PROGRAM_CHANGE: 1,
        PITCH_BENDER: 2
    }
    
    def __init__(self, event_byte, event_time):
        self.byte = event_byte
        self.time = event_time
        self.channel = -1

    def read(self, f, event_type):
        self.type = event_type
        self.data = f.read(self._data_size[self.type])
        return self

class MidiFileIO(io.FileIO):
    def __init__(self, path_to_file):
        super().__init__(path_to_file, 'rb')
        EventType = collections.namedtuple('EventType', ['begin', 'end', 'type'])
        self.event_types = {
            EventType(b'\x80', b'\x8F', MidiEvent.NOTE_OFF),
            EventType(b'\x90', b'\x9F', MidiEvent.NOTE_ON),
            EventType(b'\xB0', b'\xBF', MidiEvent.CONTROLLER_CHANGE),
            EventType(b'\xC0', b'\xCF', MidiEvent.PROGRAM_CHANGE),
            EventType(b'\xE0', b'\xEF', MidiEvent.PITCH_BENDER),
        }
        self.tracks = list()
        with self as f:
            for _ in range(f.ntracks):
                f.read_track()

    def __enter__(self, *args, **kwargs):
        f = super().__enter__(*args, **kwargs)
        form, ntracks, division = f.read_header()
        self.ntracks = ntracks
        self.format = form
        self.division = division
        return f

    def read8bit(f):
        return struct.unpack('>B', f.read(1))[0]

    def read16bit(f):
        return struct.unpack('>H', f.read(2))[0]

    def read32bit(f):
        return struct.unpack('>I', f.read(4))[0]

    def readvarint(f):
        result = 0
        for i in range(5):
            byte = f.read8bit()
            result += ((byte & 0x7F) << 7*i)
            if not(byte & 0x80 == 0x80):
                break
        return result, i+1

    def read_division(f):
        division = f.read16bit()
        if division & 0x8000 == 0x8000:
            raise DivisionFormat('SMPTE not supported')
        return division

    def read_header(f):
        chunk_type = f.read(4)
        chunk_length = f.read32bit()
        assert chunk_type == CHUNK_TYPE_HEADER
        assert chunk_length == 6
        form = f.read16bit()
        tracks = f.read16bit()
        division = f.read_division()
        print('TRACKS', tracks)
        return form, tracks, division

    def read_meta(f):
        length = 0
        bytes_read = 0
        event_type = f.read(1)
        if event_type == b'\x01':
            length, bytes_read = f.readvarint()
            txt = f.read(length)
            print('TXT', txt)
        if event_type == b'\x03':
            length, bytes_read = f.readvarint()
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
        length, bytes_read = f.readvarint()
        se = f.read(length)
        r = length+bytes_read
        print('SKIP SYSEX BYTES', r, se.hex())
        return r

    def read_event(f, event):
        if event.byte == b'\xFF':
            bytes_read = f.read_meta()
        elif event.byte == b'\xF0':
            bytes_read = f.read_sysex()
        else:
            for event_type in f.event_types:
                if event_type.begin <= event.byte <= event_type.end:
                    event.channel = ord(event.byte) - ord(event_type.begin)
                    event.read(f, event_type.type)
                    bytes_read = len(event.data)
                    break
            else:
                raise EventUnknown('Event {} not known'.format(event))
        return bytes_read
 
    def read_track(f):
        chunk_type = f.read(4)
        chunk_length = f.read32bit()
        print(chunk_type)
        assert chunk_type == CHUNK_TYPE_TRACK
        print(chunk_length)
        track = list()
        bytes_left = chunk_length
        while bytes_left != 0:
            event_time, bytes_read = f.readvarint()
            bytes_left -= bytes_read
            event_byte = f.read(1)
            if event_byte < b'\x80':
                # handle running status by moving file pointer back by 1 and set event to the running event
                f.seek(-1, io.SEEK_CUR)
                event_byte = running
                bytes_left += 1
            event = MidiEvent(event_byte, event_time)
            track.append(event)
            bytes_read = f.read_event(event)
            running = event_byte
            bytes_left -= (1+bytes_read)
        f.tracks.append(track)
        print('end of track')
        assert bytes_left == 0

path = 'Uriah_Heep_Lady_In_Black.mid'
midi = MidiFileIO(path)
print(len(midi.tracks))
