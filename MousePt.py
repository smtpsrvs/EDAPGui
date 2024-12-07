from pynput.mouse import *
from time import sleep
import win32gui
import win32con

"""
File:MousePt.py    

Description:
  Class to handles getting x,y location for a mouse click, and a routine to click on a x, y location

Author: sumzer0@yahoo.com
"""

class MousePoint:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.term = False
        self.ed_window_name = "Elite - Dangerous (CLIENT)"
        self.ls = None # Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.ms = Controller()    

    def focus_elite_window(self) -> bool:
        """Focus the Elite Dangerous window and return whether successful"""
        handle = win32gui.FindWindow(0, self.ed_window_name)
        if handle == 0:
            return False
            
        # Bring window to front and give it focus
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(handle)
        
        # Get window position and size for coordinate translation
        rect = win32gui.GetWindowRect(handle)
        self.window_x = rect[0]
        self.window_y = rect[1]
        
        sleep(0.1) # Give time for window to focus
        return True

    def on_move(self, x, y):
        return True
        
    def on_scroll(self, x, y, dx, dy):
        return True

    def on_click(self, x, y, button, pressed):
        self.x = x
        self.y = y
        self.term = True
        return True
        
    def get_location(self):
        self.focus_elite_window()  # Ensure ED window is focused
        
        self.term = False
        self.x = 0
        self.y = 0
        self.ls = Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.ls.start()
        
        try:
            while self.term == False:
                sleep(0.5)
        except:
            pass
        
        self.ls.stop()

        # Convert coordinates to be relative to ED window
        return self.x - self.window_x, self.y - self.window_y
        
    def do_click(self, x, y, delay = 0.1):
        # Focus ED window and get its position
        if not self.focus_elite_window():
            return
            
        # Convert coordinates to absolute screen position
        screen_x = self.window_x + x
        screen_y = self.window_y + y
        
        # Store current mouse position
        current_x, current_y = self.ms.position
        
        # Position the mouse and do left click
        self.ms.position = (screen_x, screen_y)
        self.ms.press(Button.left)
        sleep(delay)
        self.ms.release(Button.left)
        
        # Return mouse to original position
        self.ms.position = (current_x, current_y)


def main():
    m = MousePoint()
    m.do_click(1977,510)  
    """
    for i in range(2):
        m.do_click(1977,510)
        sleep(0.5)
    """


if __name__ == "__main__":
    main()
