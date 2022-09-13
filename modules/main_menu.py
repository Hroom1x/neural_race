import pygame
import math
import sys
import os
import pickle
import numpy as np

from modules.my_defines import *
from modules.main_classes import *

pygame.init()

__all__ = ['open_menu', 'open_settings', 'open_confirm']

def open_menu(main_sc, settings):
    pause_sc = main_sc.copy()

    clock_frame = pygame.time.Clock()

    menu_surf = pygame.Surface((1280, 720), pygame.SRCALPHA)

    pygame.draw.rect(menu_surf, (0, 0, 0, 120), (0, 0, 1280, 720))  # задний фон
    pygame.draw.rect(menu_surf, (0, 0, 0, 200), (440, 50, 400, 320))
    pygame.draw.rect(menu_surf, (0, 0, 0), (440, 50, 400, 320), 8)

    main_sc.blit(menu_surf, (0, 0))
    menu_surf = main_sc.copy()

    button_resume = menu_button(490, 90, 'Resume')
    button_restart = menu_button(490, 150, 'Restart')
    button_settings = menu_button(490, 210, 'Settings')
    button_exit = menu_button(490, 270, 'Exit')

    pygame.display.update()

    while True:

        clock_frame.tick(60)

        py_event = pygame.event.get()

        main_sc.blit(menu_surf, (0, 0))

        for event in py_event:
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        if button_resume.mouse_update(main_sc, py_event) == 1:
            return 0

        if button_restart.mouse_update(main_sc, py_event) == 1:
            return 'restart'

        if button_settings.mouse_update(main_sc, py_event) == 1:
            main_sc.blit(pause_sc, (0, 0))  # обновление экрана замороженной игры для прорисовки меню заново
            py_event = pygame.event.get()  # обнуление очереди событий
            if open_settings(main_sc, settings) == 'restart':
                return 'restart'

        if button_exit.mouse_update(main_sc, py_event) == 1:
            sys.exit()

        pygame.display.update()


def open_settings(main_sc, settings):
    clock_frame = pygame.time.Clock()

    menu_surf = pygame.Surface((1280, 720), pygame.SRCALPHA)

    pygame.draw.rect(menu_surf, (0, 0, 0, 120), (0, 0, 1280, 720))  # задний фон
    pygame.draw.rect(menu_surf, (0, 0, 0, 200), (370, 50, 540, 260))
    pygame.draw.rect(menu_surf, (0, 0, 0), (370, 50, 540, 260), 8)

    main_sc.blit(menu_surf, (0, 0))
    menu_surf = main_sc.copy()

    button_fullscreen = menu_button(400, 90, 'Fullscreen', settings_list=settings.get('fullscreen'), width=480)
    button_default = menu_button(400, 150, 'Default (restart app)', width=480)
    button_back = menu_button(400, 210, 'Back', width=235)
    button_apply = menu_button(645, 210, 'Apply', width=235)

    pygame.display.update()

    while True:

        clock_frame.tick(60)

        py_event = pygame.event.get()

        main_sc.blit(menu_surf, (0, 0))

        for event in py_event:
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        if button_fullscreen.mouse_update(main_sc, py_event) == 1:
            button_fullscreen.status_next()
            settings.get('fullscreen')[0] = button_fullscreen.status

        if button_default.mouse_update(main_sc, py_event) == 1:
            if open_confirm(main_sc) == 1:
                with open('config\\settings.pkl', 'wb') as file:
                    with open('config\\default.pkl', 'rb') as default_file:
                        default = pickle.load(default_file)
                    pickle.dump(default, file)
                return 'restart'

        if button_back.mouse_update(main_sc, py_event) == 1:
            return

        if button_apply.mouse_update(main_sc, py_event) == 1:
            if open_confirm(main_sc) == 1:
                with open('config\\settings.pkl', 'wb') as file:
                    pickle.dump(settings, file)

                if settings.get('fullscreen')[0] is False:
                    main_sc = pygame.display.set_mode((1280, 720))
                elif settings.get('fullscreen')[0] is True:
                    main_sc = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)

        pygame.display.update()


def open_confirm(main_sc):
    clock_frame = pygame.time.Clock()

    menu_surf = pygame.Surface((1280, 720), pygame.SRCALPHA)

    pygame.draw.rect(menu_surf, (0, 0, 0, 120), (0, 0, 1280, 720))
    pygame.draw.rect(menu_surf, (0, 0, 0, 200), (440, 140, 400, 200))
    pygame.draw.rect(menu_surf, (0, 0, 0), (440, 140, 400, 200), 8)

    text_font = pygame.font.Font('fonts\\bahnschrift.ttf', 36)
    text_question = text_font.render('Confirm?', 10, (150, 150, 150))
    menu_surf.blit(text_question, (570, 180))

    main_sc.blit(menu_surf, (0, 0))
    menu_surf = main_sc.copy()

    button_confirm = menu_button(460, 250, 'Confirm', width=180)
    button_cancel = menu_button(640, 250, 'Cancel', width=180)

    pygame.display.update()

    while True:

        clock_frame.tick(60)

        py_event = pygame.event.get()

        main_sc.blit(menu_surf, (0, 0))

        for event in py_event:
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        if button_confirm.mouse_update(main_sc, py_event) == 1:
            return 1

        if button_cancel.mouse_update(main_sc, py_event) == 1:
            return

        pygame.display.update()
