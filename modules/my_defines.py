import pygame
import math
import sys
import os
import pickle
import re
import numpy as np

pygame.init()

__all__ = ['check_collision', 'relu', 'relu2deriv', 'sigmoid', 'sigmoid_derivative', 'mouse_get_object',
           'draw_target_rect']

def check_collision(mask_left, rect_left,
                    mask_right, rect_right):
    x_offset = rect_right[0] - rect_left[0]
    y_offset = rect_right[1] - rect_left[1]

    return mask_left.overlap(mask_right, (x_offset, y_offset))

def mouse_get_object(object_rect):
    return object_rect.collidepoint(pygame.mouse.get_pos())

def draw_target_rect(main_sc, target_coord_x, target_coord_y, color=(255, 0, 0)):
    pygame.draw.rect(main_sc, color, (target_coord_x - 25, target_coord_y - 25, 50, 50), 3)

def _save_weights(weights, name=None):
    """if car_name is None:
                car_name = '{}'.format(self.weight_0[0])
            else:
                car_name = str(car_name)

            save_path = '{path}\\{name}.pkl'.format(path=save_path, name=car_name)

            with open(save_path, 'wb') as file:
                pickle.dump([self.weight_0, self.weight_1], file)"""
    pass

def relu(x):
    return (x > 0) * x

def relu2deriv(x):
    return x > 0

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1 - x)
