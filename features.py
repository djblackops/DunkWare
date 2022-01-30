import win32api
import win32con
import pyglet
import colors
from util import *
from entity import *
from pygame import Vector2

class Feature(object):
    def __init__(self):
        self.config = {}
        self.name = "Feature"

    def update(self):
        #Update function, runs every cheat loop when feature is enabled.
        pass


class ToggleFeature(Feature):
    def __init__(self, hotkey, pm, client, dunk, enabled=True):
        self.toggle_hotkey = hotkey
        self.enabled = enabled

        self.pm = pm
        self.client = client
        self.dunk = dunk

    def do_input(self):
        if win32api.GetAsyncKeyState(self.toggle_hotkey) & 1:
            self.enabled = not self.enabled


class DunkBhop(ToggleFeature):
    def __init__(self, hotkey, pm, client, dunk):
        super().__init__(hotkey, pm, client, dunk)
        self.name = "Bhop"

        self.jumpkey = win32con.VK_SPACE

    def update(self):
        self.do_input()
        if not self.enabled:
            return
        #self.localplayer = self.pm.read_uint(self.client + offsets.signatures["dwLocalPlayer"])
        if self.dunk.localplayer:
            if is_alive(self.pm, self.dunk.localplayer):
                if win32api.GetAsyncKeyState(self.jumpkey):
                    f_flags = self.pm.read_uint(self.dunk.localplayer + offsets.netvars["m_fFlags"])

                    if (f_flags == 256): # We are in the air
                        self.pm.write_int(self.client + offsets.signatures["dwForceJump"], 4)

                    else:
                        self.pm.write_int(self.client + offsets.signatures["dwForceJump"], 5)


class DunkNoFlash(ToggleFeature):
    def __init__(self, hotkey, pm, client, dunk):
        super().__init__(hotkey, pm, client, dunk)
        self.name = "NoFlash"

    def update(self):
        self.do_input()
        if not self.enabled:
            return
        #localplayer = self.pm.read_uint(self.client + offsets.signatures["dwLocalPlayer"])
        self.pm.write_float(self.dunk.localplayer + offsets.netvars["m_flFlashMaxAlpha"], float(0))


class DunkGhettoThirdPerson(ToggleFeature):
    def __init__(self, hotkey, pm, client, dunk):
        super().__init__(hotkey, pm, client, dunk)
        self.name = "Ghetto Thirdperson"

    def update(self):
        self.do_input()
        if not self.enabled:
            return

        #localplayer = self.pm.read_uint(self.client + offsets.signatures["dwLocalPlayer"])
        if is_alive(self.pm, self.dunk.localplayer):

            if win32api.GetAsyncKeyState(win32con.VK_XBUTTON2):
                self.pm.write_int(self.dunk.localplayer + offsets.netvars["m_iObserverMode"], 1)

            elif not win32api.GetAsyncKeyState(win32con.VK_XBUTTON2):
                self.pm.write_int(self.dunk.localplayer + offsets.netvars["m_iObserverMode"], 0)


class DunkEsp(ToggleFeature):
    def __init__(self, hotkey, pm, client, dunk):
        super().__init__(hotkey, pm, client, dunk)
        self.name = "ESP"

        self.glowObjectManager = self.pm.read_uint(self.client + offsets.signatures["dwGlowObjectManager"])

        self.config = {
            "glow": True,
            "glow_enemy_color": (1.0, 0.0, 0.0, 1.0),
            "glow_friend_color": (0.0, 0.0, 1.0, 1.0),

            "box": True,
            "box_enemy_color": colors.RED4,
            "box_friend_color": colors.CADETBLUE,

            "healthbar": True,
            "nametag": True,

            "aimlines": False,
            "aimlines_length": 400.0,
            "aimlines_color": colors.WHITE,
        }

    def grab_playername(self, entity_index):
        radar = self.pm.read_uint(
            self.pm.read_uint(self.client + offsets.signatures["dwRadarBase"]) + 0x78
        )

        player_info_table = radar + 0x2AC
        size = 0x174
        ent_player_name = ""

        try:
            ent_player_name = self.pm.read_string(player_info_table + (size * entity_index) + 0x54, 32)
        except Exception as e:
            print(e)

        return ent_player_name

    def get_frame(self, entity):
        coordinate_frame = []

        for i in range(12):
            coordinate_frame.append(self.pm.read_float(entity + offsets.netvars["m_rgflCoordinateFrame"] + 0x4 * i))

        mins = read_vec3d(self.pm, entity + offsets.netvars["m_Collision"] + 8)
        maxs = read_vec3d(self.pm, entity + offsets.netvars["m_Collision"] + 20)

        points = [
            Vector3(mins.x, mins.y, mins.z),
            Vector3(mins.x, maxs.y, mins.z),
            Vector3(maxs.x, maxs.y, mins.z),
            Vector3(maxs.x, mins.y, mins.z),
            Vector3(maxs.x, maxs.y, maxs.z),
            Vector3(mins.x, maxs.y, maxs.z),
            Vector3(mins.x, mins.y, maxs.z),
            Vector3(maxs.x, mins.y, maxs.z),
        ]
        screen_points = []

        for i in range(8):
            x, y = world_to_screen(self.dunk.viewmatrix,
                                   transform_by_matrix(points[i], coordinate_frame),
                                   self.dunk.screen_width,
                                   self.dunk.screen_height
                                   )

            screen_points.append(Vector2(x, y))

        left = screen_points[0].x
        top = screen_points[0].y
        right = screen_points[0].x
        bottom = screen_points[0].y

        for i in range(7):
            if left > screen_points[i + 1].x:
                left = screen_points[i + 1].x
            if top < screen_points[i + 1].y:
                top = screen_points[i + 1].y
            if right < screen_points[i + 1].x:
                right = screen_points[i + 1].x
            if bottom > screen_points[i + 1].y:
                bottom = screen_points[i + 1].y

        x1 = left
        x2 = right
        y1 = top
        y2 = bottom

        return x1, x2, y1, y2

    def draw_aimlines(self, entity, color):
        head_bone_position = get_bone_position(self.pm, self.pm.read_int(entity + offsets.netvars["m_dwBoneMatrix"]), 8)

        aim_angle_x = self.pm.read_float(entity + offsets.netvars["m_angEyeAnglesX"])
        aim_angle_y = self.pm.read_float(entity + offsets.netvars["m_angEyeAnglesY"])

        angle_x = aim_angle_x * math.pi / 180
        angle_y = aim_angle_y * math.pi / 180

        sin_pitch = math.sin(angle_x)
        cos_pitch = math.cos(angle_x)

        sin_yaw = math.sin(angle_y)
        cos_yaw = math.cos(angle_y)

        direction = Vector3(
            cos_pitch * cos_yaw,
            cos_pitch * sin_yaw,
            -sin_pitch
        )

        length = self.config["aimlines_length"]

        trail = Vector3(
            direction.x * length,
            direction.y * length,
            direction.z * length
        )

        eye_pos = head_bone_position + direction * 5
        trail_end = eye_pos + direction * length

        x1, y1 = world_to_screen(self.dunk.viewmatrix, eye_pos, self.dunk.screen_width, self.dunk.screen_height)
        x2, y2 = world_to_screen(self.dunk.viewmatrix, trail_end, self.dunk.screen_width, self.dunk.screen_height)

        self.dunk.overlay.meme.append(
            pyglet.shapes.Line(x1, y1, x2, y2, batch=self.dunk.overlay.batch,
                               color=remove_alpha(self.config["aimlines_color"]), width=1)
        )


    def draw_glow(self, entity, color):
        ent_glow_index = self.pm.read_int(entity + offsets.netvars["m_iGlowIndex"])
        self.pm.write_float(self.glowObjectManager + ent_glow_index * 0x38 + 0x8, float(color[0]))  # R
        self.pm.write_float(self.glowObjectManager + ent_glow_index * 0x38 + 0xC, float(color[1]))  # G
        self.pm.write_float(self.glowObjectManager + ent_glow_index * 0x38 + 0x10, float(color[2]))  # B
        self.pm.write_float(self.glowObjectManager + ent_glow_index * 0x38 + 0x14, float(color[3]))  # Alpha
        self.pm.write_int(self.glowObjectManager + ent_glow_index * 0x38 + 0x28, 1)  # Enable glow

    def draw_box(self, frame, color, line_width=2):
        (x1, x2, y1, y2) = frame

        if is_outside_screen(x1, x2, y1, y2, self.dunk.screen_width, self.dunk.screen_height):
            return

        box_width = x2-x1
        box_height = y1-y2

        batch = self.dunk.overlay.batch

        box_left = pyglet.shapes.Line(x1, y1, x1, y2, batch=batch,
                                      color=remove_alpha(color), width=line_width)
        box_right = pyglet.shapes.Line(x2, y1, x2, y2, batch=batch,
                                       color=remove_alpha(color), width=line_width)
        box_top = pyglet.shapes.Line(x1, y1, x2, y1, batch=batch,
                                     color=remove_alpha(color), width=line_width)
        box_bottom = pyglet.shapes.Line(x1, y2, x2, y2, batch=batch,
                                        color=remove_alpha(color), width=line_width)

        self.dunk.overlay.meme.extend([box_left, box_right, box_top, box_bottom])

    def draw_nametag(self, entity, entity_index, frame):
        (x1, x2, y1, y2) = frame

        box_width = x2 - x1

        name_x = x1 + box_width/2
        name_y = y1 + 10

        name_label = self.dunk.overlay.player_names[entity_index]
        name_label.x = name_x
        name_label.y = name_y
        name_label.font_size = 8

        player_name = self.grab_playername(entity_index)
        if name_label.text != player_name:
            try:
                name_label.text = player_name
            except Exception as e:
                print(e)
                name_label.text = player_name.encode("ascii", "ignore")

        self.dunk.overlay.player_names_to_draw.append(name_label)

    def draw_healthbar(self, entity, entity_index, frame):
        (x1, x2, y1, y2) = frame

        box_width = x2 - x1

        ent_health = self.pm.read_int(entity + offsets.netvars["m_iHealth"])

        hbar_width = box_width*(ent_health/100)
        hbar_height = 10
        hbar_color = colors.GREEN4

        if ent_health < 20:
            hbar_width = box_width*(20/100)

        if ent_health < 80:
            hbar_color = colors.YELLOW1

        if ent_health < 40:
            hbar_color = colors.RED2

        healthbar = pyglet.shapes.Rectangle(x1, y1, hbar_width, hbar_height, remove_alpha(hbar_color), batch=self.dunk.overlay.batch)

        self.dunk.overlay.meme.extend([healthbar])

    def update(self):
        self.do_input()
        if not self.enabled:
            return

        for entity_index, entity in self.dunk.entities.items():
            if entity == self.dunk.localplayer:
                continue

            if self.pm.read_int(entity + offsets.netvars["m_lifeState"]) or self.pm.read_bool(entity + offsets.signatures["m_bDormant"]):
                continue

            ent_team_id = self.pm.read_int(entity + offsets.netvars["m_iTeamNum"])
            # viewmatrix = dunk.viewmatrix
            # ent_origin = read_vec3d(self.pm, entity + offsets.netvars["m_vecOrigin"])
            # player_origin = read_vec3d(self.pm, entity + offsets.netvars["m_vecOrigin"])

            if self.config["glow"]:
                if ent_team_id == self.dunk.current_team:
                    self.draw_glow(entity, self.config["glow_friend_color"])
                else:
                    self.draw_glow(entity, self.config["glow_enemy_color"])

            frame = self.get_frame(entity)

            if self.config["box"]:
                if ent_team_id == self.dunk.current_team:
                    self.draw_box(frame, self.config["box_friend_color"])
                else:
                    self.draw_box(frame, self.config["box_enemy_color"])

            if self.config["nametag"]:
                self.draw_nametag(entity, entity_index, frame)

            if self.config["healthbar"]:
                self.draw_healthbar(entity, entity_index, frame)

            if self.config["aimlines"]:
                self.draw_aimlines(entity, color=colors.WHITE)