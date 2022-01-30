import pymem_pyglet as pymem
import pymem_pyglet.process
import win32process

from gl_overlay import *
from features import *

PLAYER_COLORS = {
    -2: (200, 200, 200),
    -1: (200, 200, 200),
    0: (230, 241, 61),
    1: (128, 60, 161),
    2: (16, 152, 86),
    3: (104, 163, 229),
    4: (237, 163, 56)
}

class DunkWare(object):
    def __init__(self, overlay):
        # Setup pymem
        self.pm = pymem.Pymem("csgo.exe")
        self.overlay = overlay

        self.client = pymem.process.module_from_name(self.pm.process_handle, "client.dll").lpBaseOfDll
        self.engine = pymem.process.module_from_name(self.pm.process_handle, "engine.dll").lpBaseOfDll
        self.clientState = self.pm.read_uint(self.client + offsets.signatures["dwClientState"])

        self.screen_width = self.overlay.width
        self.screen_height = self.overlay.height

        self.debugvars = {}
        self.current_team = 0
        self.entities = {}
        self.ingame = False

        self.localplayer = 0

        self.features = [
            DunkBhop(win32con.VK_NUMPAD0, self.pm, self.client, dunk=self),
            DunkNoFlash(win32con.VK_NUMPAD1, self.pm, self.client, dunk=self),
            DunkGhettoThirdPerson(win32con.VK_NUMPAD2, self.pm, self.client, dunk=self),
            DunkEsp(win32con.VK_NUMPAD3, self.pm, self.client, dunk=self)
        ]

    def update_entities(self):
        for i in range(0, 33): #0-32, 0 shouldnt be a thing but im gonna do it anyways
            entity = self.pm.read_int(self.client + offsets.signatures["dwEntityList"] + i * 0x10)
            
            if entity: 
                self.entities[i] = entity

    def get_player_color(self, entIndex):
        playerResource = self.pm.read_uint(self.client + offsets.signatures["dwPlayerResource"])
        pcolor = self.pm.read_int(playerResource+offsets.netvars["m_iCompPlayerColor"] + entIndex*0x4)

        return pcolor

    def get_current_weapon(self, entity):
        try:
            weaponHandle = self.pm.read_uint(entity + offsets.netvars["m_hActiveWeapon"]) & 0xFFF
            weapon = self.pm.read_uint(self.client + offsets.signatures["dwEntityList"] + (weaponHandle-1) * 0x10)

            weapon_id = self.pm.read_int(weapon + offsets.netvars["m_iItemDefinitionIndex"])

            if self.config.features["debug"]:
                self.debugvars["current_weapon_id"] = str(weapon_id)

            return weapon_id
        except:
            return 0

    def run(self, delta):
        self.localplayer = self.pm.read_uint(self.client + offsets.signatures["dwLocalPlayer"])
        self.glowObjectManager = self.pm.read_uint(self.client + offsets.signatures["dwGlowObjectManager"])
        self.viewmatrix = read_matrix(self.pm, self.client+offsets.signatures["dwViewMatrix"])
        
        # Iterate Entities, and add to our entity -- dict --
        self.update_entities()

        if is_alive(self.pm, self.localplayer):
            self.current_team = self.pm.read_int(self.localplayer + offsets.netvars["m_iTeamNum"])
            self.get_current_weapon(self.localplayer)

        for feature in self.features:
            feature.update()

        self.overlay.update(delta)

        self.debugvars.clear()


def main():
    # Set process priority to high, prevents some wierd stuttering
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)

    overlay = OverlayWindow("Counter-Strike: Global Offensive - Direct3D 9")
    dunk = DunkWare(overlay)

    pyglet.clock.schedule_interval(dunk.run, 1/144.0)
    pyglet.app.run()


if __name__ == '__main__':
    main()
