import os
from util import log

from model.skeleton import Root, Joint, Offset, Channel, End


class Loader:
    def __init__(self, path):
        if not os.path.exists(path):
            log("File not found:", path)
            raise FileNotFoundError
        self._path = path
        self._file = None
        self._num_frames = None
        self._idx_frame = None
        self._frame_time = None
        self._motion_data_position = None
        self._motion_header_position = None

    def read_model(self):
        log("Reading model:", self._path)
        with open(self._path, 'r') as file:
            self._read_keyword(file, "HIERARCHY")
            root = Loader._parse_root(file)
            self._motion_header_position = file.tell()
        return root

    def read_motion_header(self):
        self._file = open(self._path, 'r')
        self._file.seek(self._motion_header_position)

        self._read_keyword(self._file, "MOTION")
        self._read_keyword(self._file, "Frames:")
        self._num_frames = int(Loader._read_word(self._file))
        self._read_keyword(self._file, "Frame")
        self._read_keyword(self._file, "Time:")
        self._frame_time = float(Loader._read_word(self._file))

        self._idx_frame = 0
        self._motion_data_position = self._file.tell()
        return self._num_frames, self._frame_time

    def read_frame(self, frame_num=None):
        if frame_num is not None:
            self._file.seek(self._motion_data_position)
            for _ in range(frame_num):
                self._file.readline()
            self._idx_frame = frame_num
        line = self._file.readline()
        self._idx_frame += 1
        if not line:
            return None
        return list(map(float, line.split())), self._idx_frame

    def close_file(self):
        if self._file:
            self._file.close()

    @staticmethod
    def _parse_root(file):
        Loader._read_keyword(file, "ROOT")
        name = Loader._read_word(file)
        Loader._read_keyword(file, "{")
        offset = Loader._read_offset(file)
        channels = Loader._read_channels(file)
        root = Root(name, offset, channels)
        Loader._parse_joints(file, root)
        Loader._read_keyword(file, "}")
        return root

    @staticmethod
    def _parse_joints(file, parent):
        c = Loader._peek(file)
        while c == "J" or c == "E":
            if c == "J":
                joint = Loader._parse_joint(file, parent)
                parent.add_child(joint)
            elif c == "E":
                end = Loader._parse_end(file, parent)
                parent.add_child(end)
            c = Loader._peek(file)

    @staticmethod
    def _parse_joint(file, parent):
        Loader._read_keyword(file, "JOINT")
        name = Loader._read_word(file)
        Loader._read_keyword(file, "{")
        offset = Loader._read_offset(file)
        channels = Loader._read_channels(file)
        joint = Joint(parent, name, offset, channels)
        Loader._parse_joints(file, joint)
        Loader._read_keyword(file, "}")
        return joint

    @staticmethod
    def _parse_end(file, parent):
        Loader._read_keyword(file, "End")
        name = Loader._read_word(file)
        Loader._read_keyword(file, "{")
        offset = Loader._read_offset(file)
        Loader._read_keyword(file, "}")
        end = End(parent, name, offset)
        return end

    @staticmethod
    def _read_offset(file):
        Loader._read_keyword(file, "OFFSET")
        x = Loader._read_word(file)
        x = float(x)
        y = Loader._read_word(file)
        y = float(y)
        z = Loader._read_word(file)
        z = float(z)
        return Offset(x, y, z)

    @staticmethod
    def _read_channels(file):
        Loader._read_keyword(file, "CHANNELS")
        num_channels = Loader._read_word(file)
        num_channels = int(num_channels)
        channels = []
        for _ in range(num_channels):
            channel = Loader._read_word(file)
            if channel == "Xposition":
                channels.append(Channel.Xp)
            elif channel == "Yposition":
                channels.append(Channel.Yp)
            elif channel == "Zposition":
                channels.append(Channel.Zp)
            elif channel == "Xrotation":
                channels.append(Channel.Xr)
            elif channel == "Yrotation":
                channels.append(Channel.Yr)
            elif channel == "Zrotation":
                channels.append(Channel.Zr)
            else:
                log("Invalid channel:", channel, "in line:", file.tell())
                raise SyntaxError
        return channels

    @staticmethod
    def _read_keyword(file, keyword):
        c = file.read(1)
        while c and Loader._blank_char(c):
            c = file.read(1)
        remaining = len(keyword) - 1
        c += file.read(remaining)
        if c != keyword:
            log("Expected keyword:", keyword, "but got:", c)
            raise SyntaxError

    @staticmethod
    def _read_word(file):
        c = file.read(1)
        while c and Loader._blank_char(c):
            c = file.read(1)
        name = c
        c = file.read(1)
        while c and not Loader._blank_char(c):
            name += c
            c = file.read(1)
        return name

    @staticmethod
    def _blank_char(c):
        return c == ' ' or c == '\t' or c == '\n' or c == '\r'

    @staticmethod
    def _peek(file):
        pos = file.tell()
        c = file.read(1)
        while c and Loader._blank_char(c):
            c = file.read(1)
        file.seek(pos)
        return c
