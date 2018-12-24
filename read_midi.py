import struct
import io

CHUNK_TYPE_HEADER = b'MThd'
CHUNK_TYPE_TRACK = b'MTrk'

class DivisionFormat(Exception):
    pass
class EventUnknown(Exception):
    pass

class MidiFileIO(io.FileIO):
    def __init__(self, path_to_file):
        super().__init__(path_to_file, 'rb')
        with self as f:
            for _ in range(f.tracks):
                f.read_track()

    def __enter__(self, *args, **kwargs):
        f = super().__enter__(*args, **kwargs)
        form, tracks, division = f.read_header()
        self.tracks = tracks
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
        if division == -1:
            print('division format not supported')
            return
        print('TRACKS', tracks)
        return form, tracks, division

    def read_meta(f):
        length = 0
        bytes_read = 0
        event_type = f.read(1)
        print('EVENT TYPE', hex(ord(event_type)))
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

    def read_controller_change(f, channel):
        data = f.read(2)
        bytes_read = 2
        print('CHANNEL', channel, 'data', hex(data[0]))
        if data[0] < 0x78 or data[0] > 0x7f:
            print('CHANNEL VOICE MESSAGE on CONTROLLER', hex(data[0]), hex(data[1]))
        else:
            if data[0] == 0x79:
                reset_all_controllers()
            else:
                print('UNHANDLED CHAN MOD')
        return bytes_read

    def read_pitch_bender(f, channel):
        print('PITCH BENDER')
        data = f.read(2)
        bytes_read = 2
        return bytes_read

    def read_program_change(f, channel):
        print('PROGRAM CHANGE')
        data = f.read(1)
        bytes_read = 1
        return bytes_read

    def read_note_on(f, channel):
        data = f.read(2)
        key = hex(data[0])
        velocity = hex(data[1])
        print('NOTE ON', key, velocity)
        return 2

    def read_note_off(f, channel):
        data = f.read(2)
        key = hex(data[0])
        velocity = hex(data[1])
        print('NOTE OFF', key, velocity)
        return 2

    def read_event(f, event):
        if event == b'\xFF':
            bytes_read = f.read_meta()
        elif event == b'\xF0':
            bytes_read = f.read_sysex()
        elif b'\x80' <= event <= b'\x8F': # note on
            channel = ord(event) - ord(b'\x90')
            bytes_read = f.read_note_off(channel)
        elif b'\x90' <= event <= b'\x9F': # note on
            channel = ord(event) - ord(b'\x90')
            bytes_read = f.read_note_on(channel)
        elif b'\xB0' <= event <= b'\xBF': # controller change
            channel = ord(event) - ord(b'\xB0')
            bytes_read = f.read_controller_change(channel)
        elif b'\xB0' <= event <= b'\xBF': # controller change
            channel = ord(event) - ord(b'\xB0')
            bytes_read = f.read_controller_change(channel)
        elif b'\xC0' <= event <= b'\xCF': # program change
            channel = ord(event) - ord(b'\xC0')
            bytes_read = f.read_program_change(channel)
        elif b'\xE0' <= event <= b'\xEF': # pitch bender
            channel = ord(event) - ord(b'\xE0')
            bytes_read = f.read_pitch_bender(channel)
        else:
            raise EventUnknown('Event {} not known'.format(event))
        return bytes_read
 
    def read_track(f):
        chunk_type = f.read(4)
        chunk_length = f.read32bit()
        print(chunk_type)
        assert chunk_type == CHUNK_TYPE_TRACK
        print(chunk_length)
        bytes_left = chunk_length
        while bytes_left != 0:
            event_time, bytes_read = f.readvarint()
            print('EVENT_TIME', event_time)
            bytes_left -= bytes_read
            event = f.read(1)
            if event < b'\x80':
                # handle running status by moving file pointer back by 1 and set event to the running event
                f.seek(-1, io.SEEK_CUR)
                event = running
                bytes_left += 1
                print('RUNNING EVENT', hex(ord(event)))
            else:
                print('EVENT', hex(ord(event)))
            bytes_read = f.read_event(event)
            running = event
            bytes_left -= (1+bytes_read)
        print('end of track')
        assert bytes_left == 0

def reset_all_controllers():
    print('RESET ALL CONTROLLERS')

path = 'Uriah_Heep_Lady_In_Black.mid'
midi = MidiFileIO(path)
print(midi.tracks)
