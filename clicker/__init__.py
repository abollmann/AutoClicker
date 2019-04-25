from win32api import EnumDisplayMonitors

from definitions import *


def arith_dist(a, b):
    """ Calculate distance between to numbers. """
    if a < 0 and b > 0 or a > 0 and b < 0:
        return a + abs(b) if b < 0 else abs(a) + b
    return abs(abs(a) - abs(b))


def get_monitor_stats():
    """ Get resolution, absolute coordinates and indices of all monitors.
        Example: A 3 monitor setup like M - M - M would lead to the following indices
         [[(0, 0), (0, 1), (0, 2)],
          [(),      (),      ()],
          [(),      (),      ()]] """
    monitors = []
    for monitor in EnumDisplayMonitors():
        width = arith_dist(monitor[2][0], monitor[2][2])
        height = arith_dist(monitor[2][1], monitor[2][3])
        monitors.append({
            'resolution': (width, height),
            'width_range': (monitor[2][0], monitor[2][2]),
            'height_range': (monitor[2][1], monitor[2][3])
        })
    logging.info(msg='CONNECTED MONITORS: {}'.format(monitors))

    def calc_index(current):
        i, j = 0, 0
        for m in monitors:
            if max(m['height_range']) > max(current['height_range']):
                i += 1
            if min(m['width_range']) < min(current['width_range']):
                j += 1
        return i, j

    for monitor in monitors:
        indices = calc_index(monitor)
        monitor['indices'] = indices
    return monitors


MONITORS = get_monitor_stats()


def get_visual_setup():
    size = len(MONITORS)
    setup = [[None for _ in range(size)] for _ in range(size)]
    for monitor in MONITORS:
        i, j = monitor['indices']
        setup[i][j] = 1

    visual = ''
    for row in setup:
        if 1 not in row:
            continue
        visual = '{}{}'.format(visual, '\n')
        for entry in row:
            visual = '{}{}'.format(visual, ' M ' if entry is not None else '   ')
    return visual


def stop_listeners(listeners):
    logging.info(msg='STOPPED')
    for listener in listeners:
        listener.stop()


def get_resolution(indices):
    for monitor in MONITORS:
        if monitor['indices'] == indices:
            return monitor['resolution']


def get_monitor(x, y):
    for monitor in MONITORS:
        if min(monitor['width_range']) <= x <= max(monitor['width_range']) and \
                min(monitor['height_range']) <= y <= max(monitor['height_range']):
            return monitor
