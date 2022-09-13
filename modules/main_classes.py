import pygame
import math
import sys
import pickle
import os
import re
import numpy as np

from modules.my_defines import *

pygame.init()

__all__ = ['Car', 'User_Car', 'race_track', 'menu_button', 'neural_car']

class Car:

    def __init__(self, spawn_coord_x, spawn_coord_y, rotation=0, acceleration=0.08, max_speed=9, rotation_speed=3.6,
                 sin_cos_list=None, texture_path='images\\car.png'):
        self.texture = pygame.image.load(texture_path).convert_alpha()

        self.rotation = rotation
        self.rotation_speed = rotation_speed
        self.surf = pygame.transform.rotate(self.texture, self.rotation)

        self.mask = pygame.mask.from_surface(self.surf)

        self.size_x = self.texture.get_size()[0]
        self.size_y = self.texture.get_size()[1]
        self.prev_size_x = self.size_x
        self.prev_size_y = self.size_y

        self.coord_x = spawn_coord_x
        self.coord_y = spawn_coord_y

        self.surf_rect = self.surf.get_rect(topleft=(self.coord_x, self.coord_y))
        self.rect_offset_x = -(self.surf.get_size()[0] / 2)
        self.rect_offset_y = -(self.surf.get_size()[1] / 2)

        self.speed = 0
        self.max_speed = max_speed

        self.acceleration = acceleration  # ускорение машинки
        self.friction_acceleration = 0.04  # ускорение трения

        self.line = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        self.line_length = [0, 0, 0, 0, 0]
        self.line_angle = [-90, -135, -180, 135, 90]

        if sin_cos_list is None:
            self.sin_list = []
            self.cos_list = []
            for i in range(361):
                self.sin_list.append(round(math.sin(math.radians(i)), 3))
                self.cos_list.append(round(math.cos(math.radians(i)), 3))
        else:
            self.sin_list = sin_cos_list[0]
            self.cos_list = sin_cos_list[1]

        self.sin = self.sin_list[round(self.rotation % 360)]
        self.cos = self.cos_list[round(self.rotation % 360)]

        self.speed_x = self.speed * self.sin
        self.speed_y = self.speed * self.cos

    def move_centre(self):
        self.speed_x = self.speed * self.sin
        self.speed_y = self.speed * self.cos
        self.coord_x -= self.speed_x
        self.coord_y -= self.speed_y

        if self.speed != 0:
            if abs(self.speed) > self.friction_acceleration:
                self.speed -= self.friction_acceleration * (self.speed / abs(self.speed))
            elif abs(self.speed) < self.friction_acceleration:
                self.speed = 0

        self.surf_rect[0] = self.coord_x + self.rect_offset_x
        self.surf_rect[1] = self.coord_y + self.rect_offset_y

        self.mask = pygame.mask.from_surface(self.surf)

    def rotate_centre(self, rotate_direction):

        if rotate_direction == 'right':
            if abs(self.speed) > self.rotation_speed:
                self.rotation -= self.rotation_speed * self.speed / abs(self.speed)
            else:
                self.rotation -= self.speed
            self.surf = pygame.transform.rotate(self.texture, self.rotation)

        elif rotate_direction == 'left':
            if abs(self.speed) > self.rotation_speed:
                self.rotation += self.rotation_speed * self.speed / abs(self.speed)
            else:
                self.rotation += self.speed
            self.surf = pygame.transform.rotate(self.texture, self.rotation)

        self.sin = self.sin_list[round(self.rotation % 360)]
        self.cos = self.cos_list[round(self.rotation % 360)]

        # следующие 4 строки кода смещают картинку на половину разницы оригинального размера и настоящего.
        # это сделано для того, чтобы картинка вращалась относительно своего центра

        # переменная prev_size нужна для проверки условия предыдущего изменения координат при повороте

        self.rect_offset_x += (self.prev_size_x - self.surf.get_size()[0]) / 2
        self.prev_size_x = self.surf.get_size()[0]

        self.rect_offset_y += (self.prev_size_y - self.surf.get_size()[1]) / 2
        self.prev_size_y = self.surf.get_size()[1]

    def update_lines(self, mask):

        # меньшей нагрузки на cpu можно добиться, уменьшая длину волны (множитель перед i)
        # но при этом упадёт точность определения расстояния

        # желательно оптимизировать данный метод

        for index in range(5):

            for i in range(1, 100):
                self.line_length[index] = 3 * i

                self.line[index] = (round(self.line_length[index] *
                                          self.sin_list[round((self.rotation + self.line_angle[index]) % 360)] +
                                          self.coord_x),
                                    round(self.line_length[index] *
                                          self.cos_list[round((self.rotation + self.line_angle[index]) % 360)] +
                                          self.coord_y))

                if mask.get_at((self.line[index][0], self.line[index][1])):
                    break

        return [[self.line[0], self.line[1], self.line[2], self.line[3], self.line[4]],
                [self.line_length[0], self.line_length[1], self.line_length[2], self.line_length[3],
                 self.line_length[4]]]

    def draw_lines(self, main_sc, mask):

        lines = self.update_lines(mask)

        pygame.draw.line(main_sc, (0, 255, 0), (self.coord_x, self.coord_y), (lines[0][0]))
        pygame.draw.line(main_sc, (0, 255, 0), (self.coord_x, self.coord_y), (lines[0][1]))
        pygame.draw.line(main_sc, (0, 255, 0), (self.coord_x, self.coord_y), (lines[0][2]))
        pygame.draw.line(main_sc, (0, 255, 0), (self.coord_x, self.coord_y), (lines[0][3]))
        pygame.draw.line(main_sc, (0, 255, 0), (self.coord_x, self.coord_y), (lines[0][4]))


class User_Car(Car):
    def __init__(self, spawn_coord_x, spawn_coord_y,
                 chp_list=None, **kwargs):  # **kwargs указывает на необязательные аргументы

        super().__init__(spawn_coord_x, spawn_coord_y, **kwargs)  # наследование метода init родителя

        if chp_list is None:
            chp_list = [[(670, 570), (1, 150), 670, 635, -90]]
        self.chp_list = chp_list
        self.chp_id = 0

    def move_user(self, keys):

        self.move_centre()

        if keys[pygame.K_d] == 1:
            self.rotate_centre('right')

        elif keys[pygame.K_a] == 1:
            self.rotate_centre('left')

        if keys[pygame.K_w] == 1:
            if abs(self.speed) < self.max_speed:
                self.speed += self.acceleration

        elif keys[pygame.K_s] == 1:
            if abs(self.speed) < self.max_speed:
                self.speed -= self.acceleration

        if keys[pygame.K_SPACE] == 1:
            if abs(self.speed) > (self.acceleration * 1.7):
                self.speed -= self.acceleration * 1.7 * self.speed / abs(self.speed)

        if keys[pygame.K_r] == 1:
            self.chp_spawn()

    def next_chp(self):

        if self.chp_id < (len(self.chp_list) - 1):
            self.chp_id += 1

        elif self.chp_id == (len(self.chp_list) - 1):
            self.chp_id = 0

    def check_chp(self):

        if self.chp_id < (len(self.chp_list) - 1):
            if self.surf_rect.colliderect(pygame.Rect(self.chp_list[self.chp_id + 1][0],
                                                      self.chp_list[self.chp_id + 1][1])):
                self.next_chp()

        elif self.chp_id == (len(self.chp_list) - 1):
            if self.surf_rect.colliderect(pygame.Rect(self.chp_list[0][0],
                                                      self.chp_list[0][1])):
                self.next_chp()

    def chp_spawn(self):

        self.surf = pygame.transform.rotate(self.texture, self.rotation)

        self.speed = 0
        self.coord_x = self.chp_list[self.chp_id][2]
        self.coord_y = self.chp_list[self.chp_id][3]
        self.rotation = self.chp_list[self.chp_id][4]

        self.sin = self.sin_list[round(self.rotation % 360)]
        self.cos = self.cos_list[round(self.rotation % 360)]

        self.rect_offset_x += (self.prev_size_x - self.surf.get_size()[0]) / 2
        self.prev_size_x = self.surf.get_size()[0]

        self.rect_offset_y += (self.prev_size_y - self.surf.get_size()[1]) / 2
        self.prev_size_y = self.surf.get_size()[1]

    def restart_chp(self):
        pass

    def reverse_chp(self):
        pass


class neural_car(Car):

    def __init__(self, spawn_coord_x, spawn_coord_y, load_weights=None, **kwargs):
        super().__init__(spawn_coord_x, spawn_coord_y, **kwargs)

        self.weights = []
        self.layer_0 = [[0, 0, 0, 0, 0, 6]]  # 6 входов для пяти лучей и скорости
        self.outputs = [[[0, 0, 0, 0]]]  # 3 выхода для газа, руль влево/вправо

        if load_weights is None:
            self.weights.append(2 * np.random.random((6, 4)) - 1)

            self.weights_saved = 0
        else:
            with open(load_weights, 'rb') as file:
                loaded_weights = pickle.load(file)
                for n in loaded_weights:
                    self.weights.append(n[:])

            self.weights_saved = 1

        self.movable = 1  # способность двигаться (например, после врезания значение устанавливается на 0)
        self.target = 0  # отмеченная цель для дальнейших действий

    def think(self, inputs):
        # Не знаю, можно ли назвать данную операцию функцией активации (нет)
        # В любом случае, деление на 300 нужно для того, чтобы вход был 0 < x < 1
        inputs = inputs / 300

        # relu2deriv нужна для получения значений True/False на выходе
        self.outputs = [relu2deriv(np.dot(inputs, self.weights[0])), np.dot(inputs, self.weights[0])]

        return self.outputs

    def move_on_outputs(self):

        if self.outputs[0][0][0] == 1:
            if abs(self.speed) < self.max_speed:
                self.speed += self.acceleration

        if self.outputs[0][0][1] == 1:
            self.rotate_centre('right')

        if self.outputs[0][0][2] == 1:
            self.rotate_centre('left')

        if self.outputs[0][0][3] == 1:
            if abs(self.speed) < self.max_speed:
                self.speed -= self.acceleration

        self.move_centre()

    def mutate_weights(self, mutations_number, value):
        if mutations_number == 0:
            for layer in self.weights:
                for line in layer:
                    line[np.random.randint(3)] += (np.random.random() * 2 * value - value)
        else:
            for layer in self.weights:
                for line in layer:
                    for mut in range(len(line)):
                        line[mut] += (np.random.random() * 2 * value - value)

        self.weights_saved = 0

    def save_weights(self, car_name=None):
        if self.weights_saved == 1:
            return

        pattern = r'Saved Weights ([0-9])+\.pkl'

        if car_name is None:
            name_list = []

            for f_name in os.listdir('saved cars'):
                if re.match(pattern, f_name):
                    name_list.append(int(f_name[14:len(f_name) - 4]))

            car_name = 'Saved Weights {}'.format((max(name_list) if name_list != [] else 0) + 1)

        with open('saved cars\\{}.pkl'.format(car_name), 'wb') as file:
            pickle.dump(self.weights, file)

        self.weights_saved = 1

class race_track:

    def __init__(self, coord_x, coord_y, texture_path='maps\\track01\\track01_texture.png',
                 mask_path='maps\\track01\\track01_mask.png'):

        self.texture = pygame.image.load(texture_path).convert_alpha()
        self.surf_mask = pygame.image.load(mask_path).convert_alpha()
        self.mask = pygame.mask.from_surface(self.surf_mask)

        self.coord_x, self.coord_y = coord_x, coord_y

        self.surf_rect = self.surf_mask.get_rect(topleft=(self.coord_x, self.coord_y))


class menu_button:
    def __init__(self, coord_x, coord_y, text_in_box, settings_list=' ', width=300):

        self.settings_list = settings_list
        if type(settings_list) == list:
            self.status = settings_list[0]
        else:
            self.status = self.settings_list

        self.coord_x = coord_x
        self.coord_y = coord_y
        self.width = width

        self.rect = pygame.Rect((self.coord_x, self.coord_y), (self.width, 60))
        self.surf = pygame.Surface((1280, 60), pygame.SRCALPHA)

        self.text_font = pygame.font.Font('fonts\\bahnschrift.ttf', 36)
        self.text_in_box = self.text_font.render(text_in_box, 10, (150, 150, 150))
        self.text_status = self.text_font.render(str(self.status), 10, (150, 150, 150))

        self.surf.blit(self.text_in_box, (20, 10))
        self.surf.blit(self.text_status, (265, 10))

    def hover(self):
        pygame.draw.rect(self.surf, (80, 80, 80, 120), (0, 0, self.width, 80))
        pygame.draw.rect(self.surf, (20, 20, 20), (0, 0, self.width, 60), 6)
        self.surf.blit(self.text_in_box, (20, 10))
        self.surf.blit(self.text_status, (265, 10))

    def normal(self):
        pygame.draw.rect(self.surf, (0, 0, 0, 0), (0, 0, self.width + 10, 80))
        self.surf.blit(self.text_in_box, (20, 10))
        self.surf.blit(self.text_status, (265, 10))

    def mouse_update(self, main_sc, py_event):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            for event in py_event:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        return 1
            self.hover()
            main_sc.blit(self.surf, self.rect)
        else:
            self.normal()
            main_sc.blit(self.surf, self.rect)

    def status_next(self):
        list_index = self.settings_list[1].index(self.status)
        if list_index < (len(self.settings_list) - 1):
            self.status = self.settings_list[1][list_index + 1]
        elif list_index == (len(self.settings_list) - 1):
            self.status = self.settings_list[1][0]
        self.text_status = self.text_font.render(str(self.status), 10, (150, 150, 150))
        return self.status
