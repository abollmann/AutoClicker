import logging
import os

from pynput import keyboard


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s;%(levelname)s;%(message)s')


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 300
HEIGHT = 200

START_BUTTON = keyboard.Key.left
STOP_BUTTON = keyboard.Key.right

SAVED = 1
ABORTED = 0
