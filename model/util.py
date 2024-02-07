from vpython import vec
import numpy as np


def rotationX_mtx(theta):
    theta = np.radians(theta)
    return np.array([
        [1, 0, 0, 0],
        [0, np.cos(theta), -np.sin(theta), 0],
        [0, np.sin(theta), np.cos(theta), 0],
        [0, 0, 0, 1]])


def rotationY_mtx(theta):
    theta = np.radians(theta)
    return np.array([
        [np.cos(theta), 0, np.sin(theta), 0],
        [0, 1, 0, 0],
        [-np.sin(theta), 0, np.cos(theta), 0],
        [0, 0, 0, 1]])


def rotationZ_mtx(theta):
    theta = np.radians(theta)
    return np.array([
        [np.cos(theta), -np.sin(theta), 0, 0],
        [np.sin(theta), np.cos(theta), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]])


def translation_mtx(x, y, z):
    return np.array([
        [1, 0, 0, x],
        [0, 1, 0, y],
        [0, 0, 1, z],
        [0, 0, 0, 1]])


def set_mtx(obj, mtx):
    obj.pos = vec(mtx[0, 3], mtx[1, 3], mtx[2, 3])
    axis = length(obj.axis)
    up = length(obj.up)
    obj.axis = axis * vec(mtx[0, 0], mtx[1, 0], mtx[2, 0])
    obj.up = up * vec(mtx[0, 1], mtx[1, 1], mtx[2, 1])


def length(v):
    return np.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)