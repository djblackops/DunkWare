import numpy as np
from pygame import Vector3
import math
import offsets


def is_outside_screen(x1, x2, y1, y2, width, height):
    if x1 > width+200 or x1 < -200:
        return True
    if x2 > width+200 or x2 < -200:
        return True
    if y2 > height+200 or y2 < -200:
        return True
    if y1 > height+200 or y1 < -200:
        return True

    return False


def remove_alpha(color):
    return color[0], color[1], color[2]


def get_local_player(pm, client):
    return pm.read_uint(client+offsets.signatures["dwLocalPlayer"])


def calc_angles(src:Vector3, dest:Vector3):
    delta = src-dest
    angles = Vector3(
        math.degrees(
            float(math.atan2(-delta.z, math.sqrt(delta.x * delta.x + delta.y * delta.y)))
        ),
        math.degrees(
            float(math.atan2(delta.y, delta.x))
        ),
        0.0
    )

    return angles


def transform_by_matrix(vec, matrix):
    out = Vector3()
    arr = np.array([vec.x, vec.y, vec.z])

    out.x = np.dot(arr, np.array( [ matrix[0], matrix[1], matrix[2] ], dtype=float )) + matrix[3]
    out.y = np.dot(arr, np.array( [ matrix[4], matrix[5], matrix[6] ], dtype=float )) + matrix[7]
    out.z = np.dot(arr, np.array( [ matrix[8], matrix[9], matrix[10] ] )) + matrix[11]

    return out


def get_bone_position(pm, boneMatrix, boneID:int):
    return Vector3(
        pm.read_float(boneMatrix+0x30*boneID +0xC),
        pm.read_float(boneMatrix+0x30*boneID +0x1C),
        pm.read_float(boneMatrix+0x30*boneID +0x2C),
    )


def get_class_id(pm, entity):
    one = pm.read_uint(pm.read_uint(entity + 0x8) + 2*0x4)
    return pm.read_int(pm.read_uint(one + 0x1) + 0x14)


def world_to_screen(VIEWMATRIX, vector, width, height):
    eX = vector[0]
    eY = vector[1]
    eZ = vector[2]

    x_value = eX*VIEWMATRIX[0] + eY*VIEWMATRIX[1] + eZ*VIEWMATRIX[2] + VIEWMATRIX[3]
    y_value = eX*VIEWMATRIX[4] + eY*VIEWMATRIX[5] + eZ*VIEWMATRIX[6] + VIEWMATRIX[7]
    w_value = eX*VIEWMATRIX[12] + eY*VIEWMATRIX[13] + eZ*VIEWMATRIX[14] + VIEWMATRIX[15]
    if w_value <= 0: 
        
        w_value = 1
        #return(-200,-200)
    x_value = x_value / w_value
    y_value = y_value / w_value
 
    x_value = (width / 2 * x_value) + (x_value + width / 2)
    y_value = -(height / 2 * y_value) + (y_value + height / 2)
 
    try:
        return int(x_value), height - int(y_value)
    except Exception:
        raise ValueError("Invalid viewmatrix")


def read_matrix(pm, address):
    matrix = []
    for i in range(16):
        matrix.append(pm.read_float(address+0x4*i))

    return matrix


def read_vec3d(pm, address):
    x = pm.read_float(address)
    y = pm.read_float(address+0x4)
    z = pm.read_float(address+0x8)

    return Vector3(x, y, z)