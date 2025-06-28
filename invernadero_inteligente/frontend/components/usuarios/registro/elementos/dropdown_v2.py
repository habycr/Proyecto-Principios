import pygame
from pygame.locals import USEREVENT

class PopupMenu:
    def __init__(self, menu_data, x=100, y=100, width=150, item_height=30):
        self.menu_data = menu_data
        self.x = x
        self.y = y
        self.width = width
        self.item_height = item_height
        self.visible = False
        self.items = []
        self.rects = []
        self.font = pygame.font.Font(None, 24)
        self.selected_index = 0
        self._flatten_menu()

    def _flatten_menu(self):
        # Flatten menu structure, ignoring nested submenus
        self.items = [item for item in self.menu_data if isinstance(item, str)]
        self.rects = [pygame.Rect(self.x, self.y + i * self.item_height, self.width, self.item_height) for i in range(len(self.items))]

    def draw(self, surface):
        if not self.visible:
            return
        for i, rect in enumerate(self.rects):
            pygame.draw.rect(surface, (220, 220, 220), rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 1)
            text = self.font.render(self.items[i], True, (0, 0, 0))
            surface.blit(text, (rect.x + 5, rect.y + 5))

    def handle_event(self, event):
        if not self.visible:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    pygame.event.post(pygame.event.Event(USEREVENT, {'code': 'MENU', 'name': 'Main', 'item_id': i, 'text': self.items[i]}))
                    self.visible = False
                    return self.items[i]
        return None

    def toggle(self):
        self.visible = not self.visible

    def get_selected(self):
        return self.items[self.selected_index] if self.items else None
