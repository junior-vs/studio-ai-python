import matplotlib
import time
import pygame
from pygame.locals import *
import matplotlib.backends.backend_agg as agg
import pylab
import random
import itertools
matplotlib.use("Agg")
from genetic_algorithm import *


#### INITIALIZE WINDOW ####
# Create the Pygame window
window_size = (800, 400)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Matrix of Squares")
clock = pygame.time.Clock()




#### GLOBAL VARIABLES ####
FPS = 10
target_color = [100, 150, 200]



#### DRAW FUNCTIONS####

def draw_plot(x, y, x_label = 'Generation', y_label = 'Fitness'):
    fig = pylab.figure(figsize=[4, 4], dpi=100)
    ax = fig.gca()
    ax.plot(x, y)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    raw_data = bytes(raw_data)  # <-- conversão necessária

    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGBA")
    screen.blit(surf, (0,0))
    
    
def draw_squares(population):


    # Define the number of rows and columns in the matrix
    n = 5  # Change this value to set the size of the matrix (e.g., 5x5)
    
    # Define the size oqf each square and the distance between squares
    square_size = 50
    distance_between_squares = 10
    x_offset = 450
    y_offset = 50

    # Calculate the total size of the matrix
    matrix_size = n * (square_size + distance_between_squares) - distance_between_squares
    

    i=0
    # Draw the matrix of squares
    for row in range(n):
        for col in range(n):
            x = col * (square_size + distance_between_squares) + x_offset
            y = row * (square_size + distance_between_squares) + y_offset
            
            # pygame.draw.rect(screen, (0,0,0), (x-1, y-1, square_size+2, square_size+2))
            pygame.draw.rect(screen, (0,0,0), (x, y, square_size+1, square_size+1))
            
            pygame.draw.rect(screen, population[i], (x, y, square_size, square_size))
            i = i+1
        
    

def draw_text(screen, text, x_position, y_position, color=(255, 255, 255), font_size=30, font='Arial'):
    # Initialize Pygame font
    pygame.font.init()
    
    # Set the font and size
    font = pygame.font.SysFont(font, font_size)
    
    # Render the text
    text_surface = font.render(text, True, color)
    
    # Get the rectangle containing the text surface
    text_rect = text_surface.get_rect()
    
    # Set the position of the text
    text_rect.topleft = (x_position, y_position)
    
    # Blit the text onto the screen
    screen.blit(text_surface, text_rect)



pygame.init()
generation_counter = itertools.count(start=1)  # Start the counter at 1


# GA initialization
population = generate_random_population(population_size)
# Lists to store best fitness and generation for plotting
best_fitness_values = []
best_colors = []



# slider = Slider(50, 300, 200, screen)
# mymenu = pygame_menu.Menu('oi', 100, 100)



# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False  # Quit the game when the 'q' key is pressed
            elif event.key == pygame.K_KP1:
                target_color[0] += 1
                print(target_color)

            # elif event.key == pygame.K_KP4:
            # elif event.key == pygame.K_KP2:
            # elif event.key == pygame.K_KP5:
            # elif event.key == pygame.K_KP3:
            # elif event.key == pygame.K_KP6:
            


    i = next(generation_counter)    
    screen.fill(target_color)

    # Certifique-se de que calculate_fitness recebe os argumentos corretos
    population = sorted(population, key=lambda individual: calculate_fitness(individual, target_color))
    
    best_fitness = calculate_fitness(population[0], target_color)
    best_color = population[0]
    best_fitness_values.append(best_fitness)
    best_colors.append(best_color)

    new_population = [population[0]]  # Keep the best individual
    while len(new_population) < population_size:
        parent1, parent2 = random.choices(population[:10], k=2)
        child1, child2 = crossover(parent1, parent2)
        child1 = mutate(child1)
        child2 = mutate(child2)
        # Adiciona apenas até atingir o tamanho correto
        if len(new_population) + 2 <= population_size:
            new_population.extend([child1, child2])
        elif len(new_population) + 1 == population_size:
            new_population.append(child1)
        # Se já atingiu o tamanho, não adiciona mais

    population = new_population[:population_size]  # Garante o tamanho exato

    # Draw Methods    
    draw_plot(list(range(len(best_fitness_values))), best_fitness_values)
    draw_squares(population)
    draw_text(screen, f'Best Solution: {best_color}', 450, window_size[1]-50, font_size=15, font='Courier New')
    draw_text(screen, f'Target       : {tuple(target_color)}', 450, window_size[1]-50+15, font_size=15, font='Courier New')

    pygame.display.flip()
    clock.tick(FPS)
    
    # Garante que ambos são tuplas para comparação
    if tuple(best_color) == tuple(target_color):
        print('Cor do melhor indivíduo igual ao fundo!!!')

pygame.quit()