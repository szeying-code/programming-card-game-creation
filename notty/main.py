import os
import sys

# Make the game start from any folder: imports use "notty.…" and images/sounds use paths
# relative to this folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BASE_DIR))
os.chdir(BASE_DIR)

import pygame
from notty.ui.interface import GameInterfaceUI

"----------------------------------------Display Setting----------------------------------------"
# Set DPI Awareness for Windows **[1]**
def set_dpi_awareness():
    # Do nothing if system is not Windows
    if sys.platform != "win32":
        return
    import ctypes
    # Per-Monitor DPI Awareness
    PROCESS_PER_MONITOR_DPI_AWARE = 2
    ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

set_dpi_awareness()

# Initialize pygame
pygame.init()
# Set screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
# Create display window, scaling will respond to DPI settings
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Read actual size
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# Set title
pygame.display.set_caption("Notty")
# Create a clock to control FPS
clock = pygame.time.Clock()
FPS = 60
# Initialize UI
ui = GameInterfaceUI(screen)

"----------------------------------------Main Game Loop----------------------------------------"
def main():
    running = True # control the game loop

    while running:
        # Calculate the time passed per frame
        dt = clock.tick(FPS) / 1000.0

        # Event Handling
        for event in pygame.event.get():
            # Exit when the QUIT button / ESC key is pressed
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                break

            # Submit all events to UI logic
            ui.handle_event(event)

        # Update game logic
        ui.update(dt)

        # Draw interface
        ui.draw()

        # Refresh the screen
        pygame.display.flip()

    # Shutdown pygame
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()

"----------------------------------------Reference----------------------------------------"
"""
[1]Microsoft. SetProcessDpiAwareness function. Microsoft Learn. 
https://learn.microsoft.com/en-us/windows/win32/api/shellscalingapi/nf-shellscalingapi-setprocessdpiawareness

Python Software Foundation. ctypes — A foreign function library for Python.
https://docs.python.org/3/library/ctypes.html

The code uses ctypes.windll as described in the official ctypes documentation to call Windows API functions from Python. 
The function SetProcessDpiAwareness itself is defined by the Windows ShellScalingAPI.
"""
