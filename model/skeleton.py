from vpython import box, vec, color
from typing import List, Union, Optional
from enum import Enum, auto
from copy import deepcopy

from util import log, random_color
from model.util import rotationX_mtx, rotationY_mtx, rotationZ_mtx, translation_mtx, set_mtx


class Channel(Enum):
    Xp = auto()
    Yp = auto()
    Zp = auto()
    Xr = auto()
    Yr = auto()
    Zr = auto()


class Offset:
    def __init__(self, x: float, y: float, z: float):
        self._x = x
        self._y = y
        self._z = z

    def __str__(self):
        return f"Offset(x={self._x}, y={self._y}, z={self._z})"

    def tr_mtx(self):
        return translation_mtx(self._x, self._y, self._z)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z


class Joint:
    def __init__(self, parent: Optional[Union['Root', 'Joint']], name: str, offset: Offset, channels: List[Channel]):
        self._parent = parent
        self._children = []
        self._dof = None
        self._name = name
        self._offset_frame = offset
        self._offset_obj = None
        self._trMtx = offset.tr_mtx()
        self._channels = channels
        self._num_channels = len(channels)
        self._updatable = True
        self._obj = box(size=vec(2, 2, 2))

    def add_child(self, child: 'Joint'):
        if self._updatable:
            self._children.append(child)
        else:
            log(f"Joint({self._name}) is not updatable")
            return

    def animate(self, coordinates: List[float]):
        if len(coordinates) != self._dof:
            log("Invalid number of coordinates")
            return

        # slice coordinates to match the number of degrees of freedom of the children joints
        _coordinates = deepcopy(coordinates)
        self._actuate(_coordinates[:self._num_channels])
        _coordinates = _coordinates[self._num_channels:]
        for jnt in self._children:
            nDof = jnt.nDof
            jnt.animate(_coordinates[:nDof])
            _coordinates = _coordinates[nDof:]

    def finalize(self):
        if self._updatable:
            self._updatable = False
            self._set_obj_dimensions()
            dof = self._num_channels
            for jnt in self._children:
                dof += jnt.finalize()
            self._dof = dof
            log(f"{self._name} has {dof} degrees of freedom")
            return dof
        else:
            log(f"Joint({self._name}) is not updatable")
            raise AttributeError

    # This method calculates the transformation matrix of the joint
    def _actuate(self, coordinates):
        if self._parent is None:
            base_mtx = self._offset_frame.tr_mtx()
        else:
            base_mtx = self._parent.trMtx @ self._offset_frame.tr_mtx()  # TODO: check if this is correct
        for i, channel in enumerate(self._channels):
            if channel == Channel.Xr:
                base_mtx = base_mtx @ rotationX_mtx(coordinates[i])
            elif channel == Channel.Yr:
                base_mtx = base_mtx @ rotationY_mtx(coordinates[i])
            elif channel == Channel.Zr:
                base_mtx = base_mtx @ rotationZ_mtx(coordinates[i])
            elif channel == Channel.Xp:
                base_mtx = base_mtx @ translation_mtx(coordinates[i], 0, 0)
            elif channel == Channel.Yp:
                base_mtx = base_mtx @ translation_mtx(0, coordinates[i], 0)
            elif channel == Channel.Zp:
                base_mtx = base_mtx @ translation_mtx(0, 0, coordinates[i])
        self._trMtx = base_mtx
        base_mtx = base_mtx @ self._obj_offset_mtx()
        set_mtx(self._obj, base_mtx)

    def _set_obj_dimensions(self):
        if self._name == "Hips":
            self._obj.color = color.blue
        elif self._name == "Head":
            self._obj.color = color.red
        else:
            self._obj.color = random_color()
        if len(self._children) > 0:
            ofs = self._children[0].offset
            max_dim = max(ofs.x, ofs.y, ofs.z)
            if ofs.x == max_dim:
                self._obj.length = max_dim
                self._offset_obj = vec(max_dim / 2, 0, 0)
            elif ofs.y == max_dim:
                self._obj.height = max_dim
                self._offset_obj = vec(0, max_dim / 2, 0)
            elif ofs.z == max_dim:
                self._obj.width = max_dim
                self._offset_obj = vec(0, 0, max_dim / 2)

    def _obj_offset_mtx(self):
        ofs = self._offset_obj
        return translation_mtx(ofs.x, ofs.y, ofs.z)

    @property
    def nDof(self):
        return self._dof

    @property
    def trMtx(self):
        return self._trMtx

    @property
    def offset(self):
        return self._offset_frame


class Root(Joint):
    def __init__(self, name: str, offset: Offset, channels: List[Channel]):
        super().__init__(None, name, offset, channels)

    def finalize(self):
        dof = super().finalize()
        super().animate([0] * dof)
        return dof


class End(Joint):
    def __init__(self, parent: Union[Root, Joint], name: str, offset: Offset):
        super().__init__(parent, name, offset, [])
        self._dof = 0
        self._obj.visible = False
        self._updatable = False

    def finalize(self):
        return self._dof

    def animate(self, coordinates: List[float]):
        pass