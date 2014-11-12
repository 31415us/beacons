
import numpy as np
import pygame
import sys
import math
import serial

import beaconwrapper as bw

from Vec2D import Vec2D

PX_PER_METER = 400
WIDTH = int(3.0 * PX_PER_METER)
HEIGHT = int(2.0 * PX_PER_METER)
pygame.init()
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (255, 0, 255)

SER = serial.Serial('/dev/ttyUSB0', 19200)

def get_state():
    line = SER.readline()
    state_arr = [float(i) for i in line.split(' ')]
    robot_nr = state_arr[0]
    return (robot_nr, (state_arr[1], state_arr[2], state_arr[3], state_arr[4], state_arr[5]))

def draw_state(state, color):
    "draw a position and the covariance around it"
    (pos_x, pos_y, var_x, var_y, cov_xy) = state

    evals, evecs = np.linalg.eig(np.array([[var_x, cov_xy], [cov_xy, var_y]]))

    if evals[0] > evals[1]:
        major = 2.0*math.sqrt(5.991 * evals[0])
        minor = 2.0*math.sqrt(5.991 * evals[1])
        angle = math.atan2(evecs[:, 0][1], evecs[:, 0][0])
    else:
        major = 2.0*math.sqrt(5.991 * evals[1])
        minor = 2.0*math.sqrt(5.991 * evals[0])
        angle = math.atan2(evecs[:, 1][1], evecs[:, 1][0])

    px_pos_x = int(pos_x * PX_PER_METER)
    px_pos_y = HEIGHT - int(pos_y * PX_PER_METER)
    px_major = int(major * PX_PER_METER)
    px_minor = int(minor * PX_PER_METER)

    if px_major > 5:
        size = (0, 0, px_major, px_minor)

        e_surface = pygame.Surface((px_major, px_minor))

        pygame.draw.ellipse(e_surface, color, size, 1)

        e_surface = pygame.transform.rotate(e_surface, angle * (180.0 / math.pi))

        center_x = px_pos_x - (e_surface.get_width() / 2)
        center_y = px_pos_y - (e_surface.get_height() / 2)

        SCREEN.blit(e_surface, (center_x, center_y))

    pygame.draw.circle(SCREEN, color, (px_pos_x, px_pos_y), 0, 0)
    pygame.draw.circle(SCREEN, color, (px_pos_x, px_pos_y), 5, 1)


def main():
    "main..."

    paused = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        if not paused:
            SCREEN.fill(BLACK)

            (robot_nr, state)= get_state()

            if robot_nr == 1:
                color = RED
            else:
                color = GREEN

            draw_state(state, color)

            pygame.display.update()

if __name__ == "__main__":
    main()

