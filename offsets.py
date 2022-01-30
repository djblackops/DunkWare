import json


class OffsetPayload(object):
    def __init__(self, j):
        self.__dict__ = json.load(j)


with open("resources/offsets.json") as f:
    offsets = OffsetPayload(f)

offsets.netvars["m_iCompPlayerColor"] = 0x1CD0
offsets.netvars["m_iCompPlayerName"] = 0x09E0
