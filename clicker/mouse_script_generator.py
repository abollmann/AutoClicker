from time import time

from pynput.mouse import Button
from pynput import mouse

from definitions import *
from clicker import *

from data.setup_db import *


def start_recording(name):
    listeners = []
    start_stats = {}
    last_press_action = {}

    status = {
        'MOUSE_LISTENER_ACTIVE': False,
        'ABORTED': False
    }

    def on_click(x, y, button, pressed):
        """ Saves mouse clicks, drags and movement in general. Only left, right and
         middle (click action on mouse wheel) mouse buttons are monitored. """
        if button == Button.left:
            mouse_button = 'left'
        elif button == Button.right:
            mouse_button = 'right'
        elif button == Button.middle:
            mouse_button = 'middle'
        else:
            return True

        monitor = get_monitor(x, y)
        width, height = monitor['resolution']
        monitor_x, monitor_y = monitor['indices']

        if pressed:
            last_press_action[button] = {
                'x': x,
                'y': y,
                'time': time()
            }
        else:
            last_action = last_press_action[button]
            drag = 0 if (last_action['x'], last_action['y']) == (x, y) else 1
            delta_x = x - last_action['x']
            delta_y = y - last_action['y']
            insert_click_action(last_action['x'] / width, last_action['y'] / height,
                                monitor_x, monitor_y, drag,
                                delta_x / width, delta_y / height, mouse_button,
                                last_action['time'] - start_stats['time'], time() - last_action['time'], name)

    def on_scroll(x, y, dx, dy):
        insert_scroll_action(dy * 100, time() - start_stats['time'], name)

    def on_press(key):
        if key == START_BUTTON and not status['MOUSE_LISTENER_ACTIVE']:
            status['MOUSE_LISTENER_ACTIVE'] = True
            logging.info("STARTED")
            mouse_listener = mouse.Listener(on_click=on_click,
                                            on_scroll=on_scroll)
            listeners.append(mouse_listener)
            start_stats.update({
                'time': time()
            })
            mouse_listener.start()

        if key == STOP_BUTTON:
            if not status['MOUSE_LISTENER_ACTIVE']:
                status['ABORTED'] = True
                logging.info('ABORTED')
            else:
                stop_listeners(listeners)
            return False

    with keyboard.Listener(on_press=on_press) as keyboard_listener:
        listeners.append(keyboard_listener)
        keyboard_listener.join()
    logging.info('DONE')
    if status['ABORTED']:
        return ABORTED
    insert_mouse_script(name, get_visual_setup())
    return SAVED
