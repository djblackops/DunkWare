from util import read_vec3d
from offsets import offsets

def get_origin(pm, entity):
    return read_vec3d(pm, entity + offsets.netvars["m_vecOrigin"])

def get_distance(pm, entity1:int, entity2:int):
    origin1 = get_origin(entity1)
    origin2 = get_origin(entity2)

    return origin1.distance_to(origin2)

def get_color():
    pass

def is_teammate(pm, entity, entity2):
    return pm.read_uint(entity + offsets.netvars["m_iTeamNum"]) == pm.read_uint(entity2 + offsets.netvars["m_iTeamNum"])

def is_alive(pm, entityAddress):
    return pm.read_int(entityAddress + offsets.netvars["m_lifeState"]) == 0

def is_dormant(pm, entityAddress):
    return pm.read_bool(entityAddress + offsets.netvars["m_bDormant"])

def get_playername(pm, client, entityID):
        radar = pm.read_uint(
            pm.read_uint(client + offsets.signatures["dwRadarBase"]) + 0x78
        )
        playerInfoTable = radar+0x2AC
        size = 0x174
        ent_player_name = ""
        try:
            ent_player_name = pm.read_string(playerInfoTable + (size*entityID) +0x54, 32)
        except Exception as e:
            print(e)
            return ""

        return ent_player_name