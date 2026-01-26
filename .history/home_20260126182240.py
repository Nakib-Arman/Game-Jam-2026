# home.py
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cave Explorer")

FONT_TITLE = pygame.font.SysFont(None, 72)
FONT_BTN = pygame.font.SysFont(None, 36)

BG_COLOR = (20, 20, 20)
BTN_COLOR = (70, 70, 70)
BTN_HOVER = (120, 120, 120)
TEXT_COLOR = (255, 255, 255)

clock = pygame.time.Clock()


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, mouse_pos):
        color = BTN_HOVER if self.rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=8)

        text = FONT_BTN.render(self.text, True, TEXT_COLOR)
        screen.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def home_loop():
    buttons = [
        Button("New Game", 300, 200, 200, 50),
        Button("Continue", 300, 260, 200, 50),
        Button("Level", 300, 320, 200, 50),
        Button("Settings", 300, 380, 200, 50),
        Button("About Game", 300, 440, 200, 50),
    ]

    running = True
    while running:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if buttons[0].clicked(event):
                return "new_game"

            if buttons[4].clicked(event):
                print("Cave Explorer — survive with light & energy")

        SCREEN.fill(BG_COLOR)

        title = FONT_TITLE.render("Cave Explorer", True, TEXT_COLOR)
        SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

        for btn in buttons:
            btn.draw(SCREEN, mouse_pos)

        pygame.display.flip()
