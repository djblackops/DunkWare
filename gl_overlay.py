import win32gui
import sys
import pyglet

from entity import get_playername
from util import get_local_player

#import ctypes
#ctypes.windll.kernel32.SetLastError.argtypes = [ctypes.wintypes.DWORD]

class OverlayWindow(pyglet.window.Window):
    def __init__(self, window_title):
        self.targetHwnd = win32gui.FindWindow(None, window_title)
        if not self.targetHwnd:
            sys.exit(f"Window not found: {window_title}")

        self.targetRect = self.get_target_window_rect()
        width = self.targetRect[2] - self.targetRect[0]
        height = self.targetRect[3] - self.targetRect[1]
        print(width, height)
        
        super(OverlayWindow, self).__init__(width=width, height=height, 
        style=self.WINDOW_STYLE_OVERLAY, vsync=False)
        self.set_caption("Valve Jannies: _|_")
        self.set_location(self.targetRect[0], self.targetRect[1])
        self.width, self.height = self.get_framebuffer_size()

        pyglet.font.add_directory("resources")

        self.batch = pyglet.graphics.Batch()
        #self.fps_label = pyglet.clock.ClockDisplay()
        self.fps_label = pyglet.text.Label("", batch=self.batch)
        self.fps_label.font_name="Consolas"

        self.debug_label = pyglet.text.Label("", font_name="Consolas", multiline=True, width=400, batch=self.batch, font_size=10, anchor_y="top", anchor_x="left")
        self.debug_label.y = self.height

        self.meme = []
        self.player_names_to_draw = []

        self.player_names = {}
        self.player_names_font = ""

        for i in range(0, 33):
            self.player_names[i] = pyglet.text.Label("unconnected", font_name="HelveticaNeueLT Std Med Ext", anchor_x="center", anchor_y="bottom", font_size=8)

    def get_target_window_rect(self):
        rect = win32gui.GetWindowRect(self.targetHwnd)
        return rect

    def update_player_names(self, pm, client, entity_list):
        if get_local_player(pm, client):
            for entityID, entityAddress in entity_list.items():
                player_name = get_playername(pm, client, entityID)

                self.player_names[entityID].text = player_name

    def on_draw(self):
        self.clear()
        #for i in self.meme:
        #    i.draw()


        self.batch.draw()
        for i in list(self.meme):
            i.delete()
        
        for i in self.player_names_to_draw:
            i.draw()

        self.meme[ : ] = []
        self.player_names_to_draw[ : ] = []

    def update(self, delta):
        current_fps = str(int(pyglet.clock.get_fps()))

        self.debug_label.text = 'DunkWare'

        self.fps_label.text = current_fps


if __name__ == "__main__":
    window = OverlayWindow("")
    pyglet.clock.schedule(window.update)
    pyglet.clock.set_fps_limit(300)
    pyglet.app.run()