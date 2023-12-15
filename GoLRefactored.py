import pygame
import numpy as np
from abc import ABC, abstractmethod
#used only for message windows to save/load
from tkinter import filedialog
#used only for closing Tkinter window after save/load
import tkinter

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# Grid dimensions
n_cells_x, n_cells_y = 40, 30
cell_width = width // n_cells_x
cell_height = height // n_cells_y

# Game state
game_state = np.random.choice([0, 1], size=(n_cells_x, n_cells_y), p=[0.8, 0.2])

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
green = (0, 255, 0)

# Button dimensions
button_width, button_height = 150, 50
start_button_x, start_button_y = 10, height - button_height - 10
save_button_x, save_button_y = 460, height - button_height - 10  # save
load_button_x, load_button_y = 640, height - button_height - 10  # load


class Button(ABC):
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    @abstractmethod
    def draw(self):
        pass


class ConcreteButton(Button):
    def draw(self):
        pygame.draw.rect(screen, green, (self.x, self.y, button_width, button_height))
        font = pygame.font.Font(None, 36)
        button_text = font.render(self.text, True, black)
        text_rect = button_text.get_rect(center=(self.x + button_width // 2, self.y + button_height // 2))
        screen.blit(button_text, text_rect)


def draw_grid():
    for y in range(0, height, cell_height):
        for x in range(0, width, cell_width):
            cell = pygame.Rect(x, y, cell_width, cell_height)
            pygame.draw.rect(screen, gray, cell, 1)


def next_generation():
    global game_state
    new_state = np.copy(game_state)

    for y in range(n_cells_y):
        for x in range(n_cells_x):
            n_neighbors = game_state[(x - 1) % n_cells_x, (y - 1) % n_cells_y] + \
                           game_state[(x) % n_cells_x, (y - 1) % n_cells_y] + \
                           game_state[(x + 1) % n_cells_x, (y - 1) % n_cells_y] + \
                           game_state[(x - 1) % n_cells_x, (y) % n_cells_y] + \
                           game_state[(x + 1) % n_cells_x, (y) % n_cells_y] + \
                           game_state[(x - 1) % n_cells_x, (y + 1) % n_cells_y] + \
                           game_state[(x) % n_cells_x, (y + 1) % n_cells_y] + \
                           game_state[(x + 1) % n_cells_x, (y + 1) % n_cells_y]

            if game_state[x, y] == 1 and (n_neighbors < 2 or n_neighbors > 3):
                new_state[x, y] = 0
            elif game_state[x, y] == 0 and n_neighbors == 3:
                new_state[x, y] = 1

    game_state = new_state


def draw_cells():
    for y in range(n_cells_y):
        for x in range(n_cells_x):
            cell = pygame.Rect(x * cell_width, y * cell_height, cell_width, cell_height)
            if game_state[x, y] == 1:
                pygame.draw.rect(screen, black, cell)


global game_running_state
game_running_state = False

# Custom event for updating game state every second
UPDATE_STATE_EVENT = pygame.USEREVENT + 1
# Trigger every 1000 milliseconds (1 second)
pygame.time.set_timer(UPDATE_STATE_EVENT, 1000)


def save_game():
    root = tkinter.Tk()
    filepath = filedialog.asksaveasfilename(
        defaultextension=".npy",
        filetypes=[("Game of Life files", "*.npy"), ("All files", "*.*")],
    )
    if not filepath:
        return
    try:
        np.save(filepath, game_state)
        print("Save Game", f"The game was successfully saved under name of: {filepath}")
        root.withdraw()
    except Exception as e:
        print("Save Game", f"An error occurred: {e}")
        root.withdraw()


def load_game():
    root2 = tkinter.Tk()
    filepath = filedialog.askopenfilename(
        defaultextension=".npy",
        filetypes=[("Game of Life files", "*.npy"), ("All files", "*.*")],
    )
    if not filepath:
        return

    try:
        print("Load Game", f"The game was successfully loaded from : {filepath}")
        root2.withdraw()
        return np.load(filepath)
    except Exception as e:
        print("Load Game", f"An error occurred: {e}")
        root2.withdraw()


running = True
while running:

    screen.fill(white)
    draw_grid()
    draw_cells()

    start_button = ConcreteButton(start_button_x, start_button_y, "Start/Pause")
    save_button = ConcreteButton(save_button_x, save_button_y, "Save")
    load_button = ConcreteButton(load_button_x, load_button_y, "Load")

    start_button.draw()
    save_button.draw()
    load_button.draw()

    pygame.display.flip()

    for event in pygame.event.get():
        if (event.type == UPDATE_STATE_EVENT) & game_running_state == True:
            next_generation()
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_x <= event.pos[0] <= start_button_x + button_width and start_button_y <= event.pos[
                1] <= start_button_y + button_height:
                game_running_state = not game_running_state
            if save_button_x <= event.pos[0] <= save_button_x + button_width and save_button_y <= event.pos[
                1] <= save_button_y + button_height:
                save_game()
            if load_button_x <= event.pos[0] <= load_button_x + button_width and load_button_y <= event.pos[
                1] <= load_button_y + button_height:
                game_state = load_game()
            else:
                x, y = event.pos[0] // cell_width, event.pos[1] // cell_height
                game_state[x, y] = not game_state[x, y]

pygame.quit()
