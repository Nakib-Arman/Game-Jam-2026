# main.py
import pygame
from home import home_loop
from cave_window import run_cave

def main():
    pygame.init()
    state = "home"

    while True:
        if state == "home":
            result = home_loop()
            if result == "new_game":
                state = "cave"
            elif result == "quit":
                break

        elif state == "cave":
            run_cave()
            state = "home"

    pygame.quit()

if __name__ == "__main__":
    main()
