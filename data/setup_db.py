import sqlite3
from contextlib import contextmanager

from definitions import ROOT_DIR

DB_DIR = ROOT_DIR + '\\data\\mouse_scripts.db'


@contextmanager
def db_action():
    """ Establish new connection to avoid threading errors while generating/executing. """
    connector = sqlite3.connect(DB_DIR)
    connector.row_factory = dict_factory
    cursor = connector.cursor()
    try:
        yield cursor
    except Exception:
        connector.rollback()
        raise
    else:
        connector.commit()
    finally:
        connector.close()


def dict_factory(cursor, row):
    dictionary = {}
    for index, col in enumerate(cursor.description):
        dictionary[col[0]] = row[index]
    return dictionary


def setup():
    with db_action() as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS mouse_script (
                            name text PRIMARY KEY NOT NULL,
                            monitor_setup text NOT NULL,
                            runs integer NOT NULL,
                            pause_duration float NOT NULL
                            )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS click_action (
                            x float NOT NULL,
                            y float NOT NULL,
                            monitor_x integer NOT NULL,
                            monitor_y integer NOT NULL,
                            drag integer,
                            delta_x float,
                            delta_y float,
                            mouse_button text NOT NULL,
                            time_stamp float NOT NULL,
                            duration float NOT NULL,
                            mouse_script_name text NOT NULL,
                            FOREIGN KEY (mouse_script_name) REFERENCES mouse_script(name),
                            PRIMARY KEY (time_stamp, mouse_script_name)
                            )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS scroll_action (
                            dy integer NOT NULL,
                            time_stamp float NOT NULL,
                            mouse_script_name text NOT NULL,
                            FOREIGN KEY (mouse_script_name) REFERENCES mouse_script(name),
                            PRIMARY KEY (time_stamp, mouse_script_name)
                            )""")


def insert_mouse_script(mouse_script_name, monitor_setup, runs=1, pause_duration=1.0):
    with db_action() as cursor:
        cursor.execute("INSERT INTO mouse_script VALUES (?, ?, ?, ?)", (mouse_script_name, monitor_setup,
                                                                        runs, pause_duration))


def insert_click_action(x, y, monitor_x, monitor_y, drag, delta_x, delta_y, mouse_button, time_stamp, duration,
                        mouse_script_name):
    with db_action() as cursor:
        cursor.execute("INSERT INTO click_action VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (x, y, monitor_x, monitor_y,
                                                                                             drag, delta_x, delta_y,
                                                                                             mouse_button, time_stamp,
                                                                                             duration,
                                                                                             mouse_script_name))


def insert_scroll_action(dy, time_stamp, mouse_script_name):
    with db_action() as cursor:
        cursor.execute("INSERT INTO scroll_action VALUES (?, ?, ?)",
                       (dy, time_stamp, mouse_script_name))


def get_mouse_script(mouse_script_name):
    with db_action() as cursor:
        cursor.execute("SELECT * FROM mouse_script WHERE name=(?)", (mouse_script_name,))
        return cursor.fetchone()


def update_mouse_script(name, runs, pause_duration):
    with db_action() as cursor:
        cursor.execute("UPDATE mouse_script SET runs=(?), pause_duration=(?) WHERE name=(?) ",
                       (runs, pause_duration, name))


def delete_mouse_script(name):
    with db_action() as cursor:
        cursor.execute("DELETE FROM mouse_script WHERE name=(?)", (name,))
        cursor.execute("DELETE FROM click_action WHERE mouse_script_name=(?)", (name,))
        cursor.execute("DELETE FROM scroll_action WHERE mouse_script_name=(?)", (name,))


def get_all_mouse_script_names():
    with db_action() as cursor:
        names = cursor.execute("SELECT name FROM mouse_script").fetchall()
        return [entry['name'] for entry in names]


def get_all_click_actions(mouse_script_name):
    with db_action() as cursor:
        cursor.execute("SELECT * FROM click_action WHERE mouse_script_name=(?)", (mouse_script_name,))
        while True:
            entry = cursor.fetchone()
            if entry:
                yield entry
            else:
                break


def get_all_scroll_actions(mouse_script_name):
    with db_action() as cursor:
        cursor.execute("SELECT * FROM scroll_action WHERE mouse_script_name=(?)", (mouse_script_name,))
        while True:
            entry = cursor.fetchone()
            if entry:
                yield entry
            else:
                break
