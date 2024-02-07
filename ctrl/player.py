from vpython import canvas, button, color, vec, box, rate
from enum import Enum, auto
import os

from model.loader import Loader
from util import log


class Status(Enum):
    Unloaded = auto()
    Stopped = auto()
    Playing = auto()


class Player:
    def __init__(self, path, width=600, height=600, title="BVH Player"):
        self._path = path
        self._status = Status.Unloaded
        self._skeleton_root = None
        self._num_frames = None
        self._idx_frame = None
        self._frame_time = None
        self._rate = 500  # default rate

        # VPython drawing
        scene = canvas(title=title, width=width, height=height)
        scene.select()
        button(bind=self._start_player, text="Start", color=color.green)
        button(bind=self._stop_player, text="Stop", color=color.red)
        button(bind=self._load_and_configure_model, text="Load", color=color.blue)
        self._draw_axis()
        log("Player initialized")

    def mainloop(self):
        while True:
            rate(self._rate)
            if self._status == Status.Unloaded:
                pass
            elif self._status == Status.Playing:
                coordinates, self._idx_frame = self._loader.read_frame()
                self._skeleton_root.animate(coordinates)
            elif self._status == Status.Stopped:
                pass

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        assert isinstance(value, Status)
        self._status = value

    def _start_player(self, evt):
        if self._status == Status.Unloaded:
            log("First you need to load a BVH file")
            return
        elif self._status == Status.Playing:
            log("Player is already playing")
            pass
        elif self._status == Status.Stopped:
            self._status = Status.Playing
            f, self._idx_frame = self._loader.read_frame(self._idx_frame)
            self._skeleton_root.animate(f)
            log("Player started")

    def _stop_player(self, evt):
        if self._status == Status.Unloaded:
            log("First you need to load a BVH file")
            return
        elif self._status == Status.Stopped:
            log("Player is already stopped")
            return
        elif self._status == Status.Playing:
            self._status = Status.Stopped
            log("Player stopped")

    def _load_and_configure_model(self, evt):
        if self._status == Status.Playing or self._status == Status.Stopped:
            log("Model is already loaded and configured")
            return
        elif self._status == Status.Unloaded:
            if not os.path.exists(self._path):
                log("File not found:", self._path)
                raise FileNotFoundError
            self._loader = Loader(self._path)
            self._skeleton_root = self._loader.read_model()
            self._skeleton_root.finalize()
            self._num_frames, self._frame_time = (
                self._loader.read_motion_header())
            self._rate = int(1 / self._frame_time)
            coordinates = self._loader.read_frame()
            self._skeleton_root.animate(coordinates)
            log("Model loaded and configured")
            self._status = Status.Stopped
            return

    @staticmethod
    def _draw_axis():
        box(pos=vec(50, 0, 0), length=100, height=0.5, width=0.5, color=color.red)
        box(pos=vec(0, 50, 0), length=0.5, height=100, width=0.5, color=color.green)
        box(pos=vec(0, 0, 50), length=0.5, height=0.5, width=100, color=color.blue)
