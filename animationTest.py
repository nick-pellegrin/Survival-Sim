import pygame
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import multiprocessing as mp
import nengo
import sys
from random import *

# Global Game Constants
WIN_WIDTH = 1500
WIN_HEIGHT = 1000
BACKGROUND_COLOR = (30, 30, 30)

# Global Prey Constants
DEFAULT_PREY_SPEED = 1
DEFAULT_PREY_ALERT_SPEED = 3
DEFAULT_PREY_FORCE = 0.18
DEFAULT_PREY_ALERT_FORCE = 0.3
MAX_PREY_POP = 35

# Global Predator Constants
DEFAULT_PRED_SPEED = 3.3
DEFAULT_PRED_FORCE = 0.3
MAX_PRED_POP = 10

# Global Food Constants
MAX_FOOD_COUNT = 200

#initializes the module packages and the screen
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
screen.fill(BACKGROUND_COLOR)





def get_dist(pos1, pos2):
    dist = np.linalg.norm(pos1 - pos2)
    return dist






class Food:
    def __init__(self, x, y):
        self.position = np.array([float(x), float(y)])
        self.size = 1
        self.is_eaten = False

    def draw(self):
        pygame.draw.circle(screen, (0, 255, 0), self.position, self.size)










class Prey:
    def __init__(self, x, y):
        self.position = np.array([float(x), float(y)])
        self.velocity = (np.random.rand(2) - 0.5)*10      # -5.0 < velocity < 5.0       -> [x, y]
        self.acceleration = (np.random.rand(2) - 0.5)/2   # -0.25 < acceleration < 0.25 -> [x, y]
        self.max_force = DEFAULT_PREY_FORCE   #default: 0.3
        self.max_speed = DEFAULT_PREY_SPEED     #default: 3
        self.alert_radius = 150
        self.avoidance_perception = 30
        self.is_dead = False
        self.food_counter = 0
        self.size = 3
        self.color = (200, 200, 200)

    def draw(self):
        pygame.draw.circle(screen, self.color, self.position, self.size)
        # pygame.draw.circle(screen, (0, 0, 0), self.position, self.alert_radius, 1)

    def avoid_edges(self, width, height, margin):
        acceleration = np.zeros(2)
        x, y = self.position
        if x < margin:
            acceleration[0] = (margin - x) / margin
        elif x > width - margin:
            acceleration[0] = (width - margin - x) / margin
        if y < margin:
            acceleration[1] = (margin - y) / margin
        elif y > height - margin:
            acceleration[1] = (height - margin - y) / margin
        if np.linalg.norm(acceleration) > 0:
            acceleration = (acceleration/np.linalg.norm(acceleration)) * self.max_speed
            acceleration = acceleration - self.velocity
            if np.linalg.norm(acceleration) > self.max_force:
                acceleration = (acceleration/np.linalg.norm(acceleration)) * self.max_force
        self.acceleration += acceleration

    def edges(self):
        if self.position[0] > WIN_WIDTH:
            self.position[0] = 0
        elif self.position[0] < 0:
            self.position[0] = WIN_WIDTH
        if self.position[1] > WIN_HEIGHT:
            self.position[1] = 0
        elif self.position[1] < 0:
            self.position[1] = WIN_HEIGHT

    def move(self, pred_pop, prey_pop, food_source):
        # self.avoid_edges(WIN_WIDTH, WIN_HEIGHT, 50)
        self.edges()
        self.apply_behavior(pred_pop, prey_pop, food_source)
        self.update()
        self.draw()
        self.acceleration = np.array([0.0, 0.0])  #resets acceleration vector

    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration

    def apply_behavior(self, pred_pop, prey_pop, food_source):
        avoid = self.avoid_pred(pred_pop)
        if np.linalg.norm(avoid) > 0:
            self.max_speed = DEFAULT_PREY_ALERT_SPEED
            self.max_force = DEFAULT_PREY_ALERT_FORCE
            self.acceleration += avoid
        else:
            self.max_speed = DEFAULT_PREY_SPEED
            self.max_force = DEFAULT_PREY_FORCE
            self.acceleration += self.eat_food(food_source)
            self.acceleration += self.avoid_other_prey(prey_pop)

    def avoid_pred(self, pop):
        steering = np.zeros(2)
        for entity in pop:
            if get_dist(self.position, entity.position) <= self.alert_radius:
                steering += (self.position - entity.position)
        if np.linalg.norm(steering) > 0:
            steering = (steering/np.linalg.norm(steering)) * self.max_speed
            steering = steering - self.velocity
            if np.linalg.norm(steering) > self.max_force:
                steering = (steering/np.linalg.norm(steering)) * self.max_force
        return steering
    
    def avoid_other_prey(self, prey_pop):
        steering = np.array([0.0, 0.0])
        total = 0
        for prey in prey_pop:
            if prey != self and np.linalg.norm(prey.position - self.position) < self.avoidance_perception:
                difference = self.position - prey.position
                difference /= np.linalg.norm(prey.position - self.position)
                steering += difference
                total += 1
        if total > 0:
            steering /= total
            if np.linalg.norm(steering) > 0:
                steering = (steering / np.linalg.norm(steering)) * self.max_speed
            steering = steering - self.velocity
        if np.linalg.norm(steering) > self.max_force:
            steering = (steering/np.linalg.norm(steering)) * self.max_force
        return steering
    
    def eat_food(self, pop):
        nearest = 5000
        target = pop[0]
        for entity in pop:
            if get_dist(self.position, entity.position) < nearest:
                target = entity
                nearest = get_dist(self.position, entity.position)
        if nearest <= 2:
            target.is_eaten = True
            self.food_counter += 1
        steering = ((target.position - self.position)/get_dist(target.position, self.position)) * self.max_speed
        steering = steering - self.velocity
        if np.linalg.norm(steering) > self.max_force:
            steering = (steering/np.linalg.norm(steering)) * self.max_force
        return steering
            












class Predator:
    def __init__(self, x, y):
        self.position = np.array([float(x), float(y)])
        self.velocity = (np.random.rand(2) - 0.5)*10      # -5.0 < velocity < 5.0       -> [x, y]
        self.acceleration = (np.random.rand(2) - 0.5)/2   # -0.25 < acceleration < 0.25 -> [x, y]
        self.max_force = DEFAULT_PRED_FORCE   #default: 0.3
        self.max_speed = DEFAULT_PRED_SPEED     #default: 3.3
        self.food_counter = 0
        self.avoidance_perception = 100
        self.size = 4
        self.color = (255, 0, 50)

    def draw(self):
        pygame.draw.circle(screen, self.color, self.position, self.size)
        # pygame.draw.circle(screen, (255, 0, 0), self.position, self.range, 1)

    def edges(self):
        if self.position[0] > WIN_WIDTH:
            self.position[0] = 0
        elif self.position[0] < 0:
            self.position[0] = WIN_WIDTH
        if self.position[1] > WIN_HEIGHT:
            self.position[1] = 0
        elif self.position[1] < 0:
            self.position[1] = WIN_HEIGHT

    def move(self, prey_pop, pred_pop):
        # self.avoid_edges(WIN_WIDTH, WIN_HEIGHT, 100)
        self.edges()
        self.apply_behavior(prey_pop, pred_pop)
        self.update()
        self.draw()
        self.acceleration = np.array([0.0, 0.0])  #resets acceleration vector
        
    def update(self):
        self.position += self.velocity
        self.velocity += self.acceleration

    def apply_behavior(self, prey_pop, pred_pop):
        self.acceleration += self.hunt(prey_pop)
        self.acceleration += self.avoid_other_pred(pred_pop)

    def hunt(self, prey_pop):
        nearest = 5000
        target = prey_pop[0]
        for entity in prey_pop:
            if get_dist(self.position, entity.position) < nearest:
                target = entity
                nearest = get_dist(self.position, entity.position)
        if nearest <= 3:
            target.is_dead = True
            self.food_counter += 1
        steering = ((target.position - self.position)/get_dist(target.position, self.position)) * self.max_speed
        steering = steering - self.velocity
        if np.linalg.norm(steering) > self.max_force:
            steering = (steering/np.linalg.norm(steering)) * self.max_force
        return steering
    
    def avoid_other_pred(self, pred_pop):
        steering = np.array([0.0, 0.0])
        total = 0
        for pred in pred_pop:
            if pred != self and np.linalg.norm(pred.position - self.position) < self.avoidance_perception:
                difference = self.position - pred.position
                difference /= np.linalg.norm(pred.position - self.position)
                steering += difference
                total += 1
        if total > 0:
            steering /= total
            if np.linalg.norm(steering) > 0:
                steering = (steering / np.linalg.norm(steering)) * self.max_speed
            steering = steering - self.velocity
        if np.linalg.norm(steering) > self.max_force:
            steering = (steering/np.linalg.norm(steering)) * self.max_force
        return steering










def run_game():

    #Initialize Predator, Prey, and Food populations
    prey_population = []
    for i in range(20): prey_population.append(Prey(randint(150, 1350), randint(150, 850)))
    pred_population = []
    for i in range(3): pred_population.append(Predator(randint(150, 1350), randint(150, 850)))
    food_source = []
    for i in range(100): food_source.append(Food(randint(150, 1350), randint(150, 850)))

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.fill(BACKGROUND_COLOR)
        
        # Check if food has been eaten
        for food in food_source:
            if food.is_eaten is True:
                food_source.remove(food)
            food.draw()

        # Remove dead prey, move surviving prey, spawn new prey if they eat enough
        for prey in prey_population:
            if prey.is_dead is True:
                prey_population.remove(prey)
            if prey.food_counter >= 10:
                if len(prey_population) <= MAX_PREY_POP:
                    prey_population.append(Prey(randint(150, 1350), randint(150, 850)))
                prey.food_counter = 0
            prey.move(pred_population, prey_population, food_source)

        # Move the predators
        for pred in pred_population:
            if pred.food_counter >= 5:
                if len(pred_population) <= MAX_PRED_POP:
                    pred_population.append(Predator(randint(150, 1350), randint(150, 850)))
                pred.food_counter = 0
            pred.move(prey_population, pred_population)
            
        # Spawn new food throughout the simulation
        if randint(0, 10) < 2 and len(food_source) <= MAX_FOOD_COUNT:
            food_source.append(Food(randint(150, 1350), randint(150, 850)))
        
        
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()











if __name__ == '__main__':
    run_game()
    # sim_process = mp.Process(target=run_game)
    # sim_process.start()
    # sim_process.join()



    # #graph animation stuff
    # fig, ax = plt.subplots()

    # x = np.arange(0, 6*np.pi, 0.01)
    # line, = ax.plot(x, np.sin(x))


    # def animate(i):
    #     line.set_ydata(np.sin(x + i / 50))  # update the data.
    #     return line,

    # ani = animation.FuncAnimation(fig, animate, interval=20, blit=True, save_count=50)

    # plt.show()