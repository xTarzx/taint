from typing import List
import pygame
import tkinter
import tkinter.filedialog
from tkinter.messagebox import askokcancel
from tkinter.colorchooser import askcolor


class COLORS:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


def prompt_file():
    top = tkinter.Tk()
    top.withdraw()
    file_name = tkinter.filedialog.asksaveasfilename(
        parent=top, filetypes=[("PNG", ".png")])
    return file_name


def prompt_color():
    top = tkinter.Tk()
    top.withdraw()
    color = askcolor(color=None)[0]
    top.destroy()
    return color


def prompt_clear():
    top = tkinter.Tk()
    top.withdraw()
    val = askokcancel(message="Confirm clear")
    top.destroy()
    return val


window_width, window_height = 1024, 576
SIZE = 32
N = 15


class Button(pygame.Rect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, screen):
        ...


class PickerButton(Button):
    def draw(self, screen):
        o = 5
        pygame.draw.rect(screen, COLORS.WHITE, self, 1)
        pygame.draw.line(screen, COLORS.WHITE, (self.centerx,
                         self.top+o), (self.centerx, self.bottom-o), 3)
        pygame.draw.line(screen, COLORS.WHITE, (self.left+o,
                         self.centery), (self.right-o, self.centery), 3)


class ClearButton(Button):
    def draw(self, screen):
        o = 5
        pygame.draw.rect(screen, COLORS.WHITE, self, 1)
        pygame.draw.line(screen, COLORS.WHITE,
                         (self.left+o, self.top+o), (self.right-o, self.bottom-o), 3)
        pygame.draw.line(screen, COLORS.WHITE,
                         (self.left+o, self.bottom-o), (self.right-o, self.top+o), 3)


class Block(pygame.Rect):
    def __init__(self, *args, color=COLORS.WHITE, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color


class Canvas(pygame.Surface):
    def __init__(self):
        super().__init__((N*SIZE, N*SIZE))
        self.blocks: List[Block] = []
        self.show_grid = 0
        self.init_canvas()
        self.update()

    def paint(self, pos, color):
        for block in self.blocks:
            if block.collidepoint(pos):
                block.color = color
                break

    def toggle_grid(self):
        self.show_grid = 1 - self.show_grid

    def update(self):
        self.fill(COLORS.BLACK)
        self.draw_rects()
        if self.show_grid:
            self.draw_grid()

    def init_canvas(self):
        for x in range(0, self.get_width(), SIZE):
            for y in range(0, self.get_height(), SIZE):
                self.blocks.append(Block(x, y, SIZE, SIZE))

    def draw_rects(self):
        for block in self.blocks:
            pygame.draw.rect(self, block.color, block)

    def draw_grid(self):
        for v in range(0, self.get_width(), SIZE):
            pygame.draw.line(self, COLORS.BLACK, (v, 0),
                             (v, self.get_height()))
            pygame.draw.line(self, COLORS.BLACK, (0, v), (self.get_width(), v))

    def clear(self):
        for block in self.blocks:
            block.color = COLORS.WHITE


class Palette:
    def __init__(self, offset, colors):
        self.blocks: List[Block] = []
        self.offset = offset
        self.colors = colors
        self.init_palette()
        self.button_add = PickerButton(self.offset, 0, SIZE, SIZE)
        self.button_clear = ClearButton(self.offset+SIZE, 0, SIZE, SIZE)
        self.selected = 0
        self.color_selected = (255, 213, 0)

    @property
    def color(self):
        return self.blocks[self.selected].color

    def select(self, pos):
        if self.button_add.collidepoint(pos):
            color = prompt_color()
            if color:
                self.add_color(color)

        elif self.button_clear.collidepoint(pos):
            ok = prompt_clear()
            if ok:
                self.canvas.clear()

        else:
            for idx, block in enumerate(self.blocks):
                if block.collidepoint(pos):
                    self.selected = idx

    def add_color(self, color):
        self.colors.append(color)
        self.init_palette()

    def init_palette(self):
        y = 0
        x = 0
        for idx, color in enumerate(self.colors):
            if (idx/3).is_integer():
                y += SIZE
                x = 0
            self.blocks.append(Block(self.offset+x,
                               y, SIZE, SIZE, color=color))
            x += SIZE

    def draw(self, screen):
        for idx, block in enumerate(self.blocks):
            pygame.draw.rect(screen, block.color, block)
            if idx == self.selected:
                pygame.draw.rect(screen, self.color_selected, block, 1)

        self.button_add.draw(screen)
        self.button_clear.draw(screen)

    def bind_canvas(self, canvas):
        self.canvas = canvas


pygame.init()
pygame.display.set_caption("Taint")
img = pygame.image.load("pencil_tranparent.png")
pygame.display.set_icon(img)
screen = pygame.display.set_mode((window_width, window_height))
clock = pygame.time.Clock()

canvas = Canvas()
palette = Palette(window_width-200,
                  [COLORS.RED, COLORS.GREEN, COLORS.BLUE, COLORS.WHITE, COLORS.BLACK])
palette.bind_canvas(canvas)

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                run = False

            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                filename = prompt_file()
                if filename:
                    pygame.image.save(canvas, filename)

            elif event.key == pygame.K_g:
                canvas.toggle_grid()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                palette.select(event.pos)

    mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    if mouse_buttons[0]:
        if canvas.get_rect().collidepoint(mouse_pos):
            canvas.paint(mouse_pos, palette.color)

    canvas.update()
    screen.fill((63, 63, 63))
    palette.draw(screen)
    screen.blit(canvas, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
