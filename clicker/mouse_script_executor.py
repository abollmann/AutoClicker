from time import time
from threading import Thread

import pyautogui as auto_mouse
from pywinauto import mouse as pywin_mouse

from clicker import get_resolution, stop_listeners
from data.setup_db import *
from definitions import *


def start_executing(name, runs, pause_duration):

    listeners = []

    status = {
        'STARTED': False,
        'STOPPED': False,
        'ABORTED': False
    }

    def execute_mouse_clicks():
        logging.info('Starting click actions')
        start_time = time()
        for entry in get_all_click_actions(name):
            while time() - start_time < entry['time_stamp']:
                if status['STOPPED']:
                    return
            x = entry['x']
            y = entry['y']
            width, height = get_resolution((entry['monitor_x'], entry['monitor_y']))
            pywin_mouse.move((int(x * width), int(y * height)))
            if entry['drag'] == 1:
                auto_mouse.drag(xOffset=entry['delta_x'] * width, yOffset=entry['delta_y'] * height,
                                duration=entry['duration'], button=entry['mouse_button'])
            else:
                auto_mouse.click(duration=entry['duration'], button=entry['mouse_button'])

    def execute_mouse_scrolls():
        logging.info('Starting scroll actions')
        start_time = time()
        for entry in get_all_scroll_actions(name):
            while time() - start_time < entry['time_stamp']:
                if status['STOPPED']:
                    return
            auto_mouse.scroll(entry['dy'])

    def start_recreation():
        Thread(target=start_recreation_threads).start()

    def start_recreation_threads():
        for i in range(runs):
            logging.info('RUN: {}'.format(i + 1))
            mouse_scrolls = Thread(target=execute_mouse_scrolls)
            mouse_clicks = Thread(target=execute_mouse_clicks)
            mouse_scrolls.start()
            mouse_clicks.start()
            while True:
                if not mouse_scrolls.is_alive() and not mouse_clicks.is_alive():
                    death_time = time()
                    if not status['STOPPED'] and i < runs - 1:
                        logging.info('Waiting for next run')
                        # wait for pause_duration seconds
                    while time() - death_time < pause_duration:
                        if status['STOPPED']:
                            # abort
                            logging.info('STOPPED!')
                            stop_listeners(listeners)
                            return
                    # resume next run
                    break
        stop_listeners(listeners)

    def on_press(key):
        if key == START_BUTTON and not status['STARTED']:
            status['STARTED'] = True
            logging.info("START!")
            logging.info('runs: {}, interval: {}'.format(runs, pause_duration))
            start_recreation()

        if key == STOP_BUTTON:
            if status['STARTED']:
                status['STOPPED'] = True
            else:
                status['ABORTED'] = True
                logging.info('ABORTED')
                return False

    with keyboard.Listener(on_press=on_press) as keyboard_listener:
        listeners.append(keyboard_listener)
        keyboard_listener.join()
    logging.info('DONE')
    if not status['ABORTED']:
        update_mouse_script(name, runs, pause_duration)
