import pygame
import math
import sys
import os
import pickle
import re
import numpy as np

from modules import *

pygame.init()
try:
    with open('config\\settings.pkl', 'rb') as file:
        settings = pickle.load(file)
except FileNotFoundError:
    with open('config\\default.pkl', 'rb') as file:
        settings = pickle.load(file)
    with open('config\\settings.pkl', 'wb') as file:
        pickle.dump(settings, file)

os.environ['SDL_VIDEO_CENTERED'] = '1'  # положение окна приложения
if settings.get('fullscreen')[0] is False:
    main_sc = pygame.display.set_mode((1280, 720))
elif settings.get('fullscreen')[0] is True:
    main_sc = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
pygame.display.set_caption('Neural Network Race')

clock_frame = pygame.time.Clock()  # переменная для создания ограничения частоты кадров

font1 = pygame.font.Font('fonts\\bahnschrift.ttf', 16)

sin_list = []
cos_list = []
for i in range(361):
    sin_list.append(round(math.sin(math.radians(i)), 3))
    cos_list.append(round(math.cos(math.radians(i)), 3))

pygame.display.update()


def main_process():
    real_ticks = pygame.time.get_ticks()
    clock_update_70ms = real_ticks
    clock_update_100ms = real_ticks

    # np.random.seed(1) сид генерации (потом включу для контролируемого обучения

    text_surf = pygame.Surface((1280, 720), pygame.SRCALPHA)

    chp_list = [[(670, 570), (1, 150), 670, 635, -90],
                [(1120, 240), (150, 1), 1185, 240, 0],
                [(580, 250), (150, 1), 645, 250, 10],
                [(220, 360), (1, 150), 220, 425, 90]]

    player1 = User_Car(670, 635, rotation=-90, chp_list=chp_list, sin_cos_list=[sin_list, cos_list])
    cars = [
        neural_car(670, 635, rotation=-90)
    ]
    # cars[0].target = 1
    # for n in range(1, len(cars)):
    #     cars[n].mutate_weights(0, 0.08)
    track = race_track(0, 0)  # карта (трасса)

    draw_lines = False

    while True:
        clock_frame.tick(60)  # задаём кол-во кадров в секунду
        real_ticks = pygame.time.get_ticks()

        keys = pygame.key.get_pressed()

        for n in cars:
            if n.movable == 1:
                if (real_ticks - clock_update_70ms) > 70:
                    for x in cars:
                        inputs = x.update_lines(track.mask)[1]
                        inputs.append(x.speed)
                        x.think(np.array([inputs]))
                    clock_update_70ms = real_ticks

                n.move_on_outputs()

        player1.move_user(keys)
        player1.check_chp()

        for n in range(len(cars)):
            if cars[n].speed != 0:
                if check_collision(cars[n].mask, cars[n].surf_rect, track.mask, track.surf_rect) is not None:
                    cars[n].speed = 0
                    cars[n].movable = 0

        if player1.speed != 0:
            if check_collision(player1.mask, player1.surf_rect, track.mask, track.surf_rect) is not None:
                player1.speed = 0

        main_sc.blit(track.texture, track.surf_rect)
        for n in cars:
            main_sc.blit(n.surf, n.surf_rect)
            if n.target == 1:
                if n.weights_saved == 0:
                    draw_target_rect(main_sc, n.coord_x, n.coord_y)
                else:
                    draw_target_rect(main_sc, n.coord_x, n.coord_y, color=(0, 255, 0))
        main_sc.blit(player1.surf, player1.surf_rect)

        if (real_ticks - clock_update_100ms) > 100:
            text_car_speed = font1.render('speed    ' + str(round(player1.speed, 1)), 10, (255, 255, 255))
            text_fps = font1.render('fps    ' + str(round(clock_frame.get_fps(), 2)), 10, (255, 255, 255))
            text_mouse_pos = font1.render('mouse   ' + str(pygame.mouse.get_pos()), 10, (255, 255, 255))

            pygame.draw.rect(text_surf, (0, 0, 0, 90), (0, 0, 150, 100))

            text_surf.blit(text_car_speed, (10, 20))
            text_surf.blit(text_fps, (10, 40))
            text_surf.blit(text_mouse_pos, (10, 60))

            clock_update_100ms = pygame.time.get_ticks()

        if draw_lines is True:
            player1.draw_lines(main_sc, track.mask)

        main_sc.blit(text_surf, (0, 0))

        for py_event in pygame.event.get():

            if py_event.type == pygame.QUIT:
                sys.exit()

            if py_event.type == pygame.KEYDOWN:
                if py_event.key == pygame.K_ESCAPE:
                    if open_menu(main_sc, settings) == 'restart':
                        return 'restart'

                if py_event.key == pygame.K_1:
                    draw_lines = not draw_lines

                if py_event.key == pygame.K_F5:
                    for n in cars:
                        if n.target == 1:
                            n.save_weights()

            if py_event.type == pygame.MOUSEBUTTONDOWN:
                if py_event.button == 1:
                    for n in cars:
                        if mouse_get_object(n.surf_rect):
                            n.target = not n.target

        pygame.display.update()  # оптимизировать путём "dirty_rects"


if __name__ == '__main__':
    while True:
        result = main_process()
        if result != 'restart':
            break
