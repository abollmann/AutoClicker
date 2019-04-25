from tkinter import *

from ui.tooltips import CreateToolTip
from data.setup_db import *
from definitions import *
from clicker.mouse_script_executor import start_executing
from clicker.mouse_script_generator import start_recording
from clicker import get_visual_setup

PLACE_HOLDERS = {'no_mouse_scripts': 'No mouse scripts yet',
                 'select_script': 'Select a mouse script'}

ASSETS_DIR = ROOT_DIR + '\\assets\\'


@contextmanager
def ignore_exception(exception):
    try:
        yield
    except exception:
        pass


def set_text(widget, text, color='black'):
    widget.config(fg=color)
    widget.delete(0, 'end')
    widget.insert(0, text)


def check_for_script(func):
    """ Decorator for mouse script actions. Checks if script exists. """
    def check(script_name):
        if get_mouse_script(script_name):
            func(script_name)
        else:
            print('"{}" does not exist!'.format(script_name))
    return check


def check_inputs(entry, expected_type):
    try:
        data = expected_type(entry.get())
        return data
    except ValueError:
        error_msg = '{} required!'.format(expected_type)
        set_text(entry, error_msg, color='red')
        raise


def generate_unique_mouse_script_name(mouse_script_name):
    mouse_script_names = get_all_mouse_script_names()
    new_name = mouse_script_name
    # unique identifier
    identifier = 0
    while new_name in mouse_script_names:
        identifier += 1
        new_name = mouse_script_name + '_{}'.format(identifier)
    return new_name


def create_option_menu(value_string=None):
    """ Create or refresh the dropdown menu. """

    @check_for_script
    def adjust_settings(mouse_script_name):
        """ Load script settings that were last used. """
        mouse_script_data = get_mouse_script(mouse_script_name)
        set_text(runs_entry, mouse_script_data['runs'])
        set_text(pause_duration_entry, mouse_script_data['pause_duration'])

        # refresh info
        info_tool_tip = 'Used monitor setup: {}'.format(mouse_script_data['monitor_setup'])
        CreateToolTip(info_button, info_tool_tip)

    mouse_script_names = get_all_mouse_script_names()
    if value_string is not None:
        adjust_settings(value_string)
    else:
        if not mouse_script_names:
            mouse_script_names.append(PLACE_HOLDERS['no_mouse_scripts'])
            value_string = PLACE_HOLDERS['no_mouse_scripts']
        else:
            value_string = PLACE_HOLDERS['select_script']
            with ignore_exception(ValueError):
                mouse_script_names.remove(PLACE_HOLDERS['no_mouse_scripts'])

    dropdown_value.set(value_string)
    option_menu = OptionMenu(main_frame, dropdown_value, *mouse_script_names,
                             command=adjust_settings)
    option_menu.grid_configure(row=0, column=0, padx=5, pady=2, columnspan=10, sticky=W)
    CreateToolTip(info_button, value_string)


@check_for_script
def start_script(mouse_script_name):
    """ Minimize app to task bar and start the selected script. """
    with ignore_exception(ValueError):
        runs = check_inputs(runs_entry, int)
        pause_duration = check_inputs(pause_duration_entry, float)
        start_tool_tip.close()
        app.wm_state('iconic')
        start_executing(mouse_script_name, runs, pause_duration)


@check_for_script
def delete_script(mouse_script_name):
    delete_mouse_script(mouse_script_name)
    create_option_menu()
    set_text(pause_duration_entry, '')
    set_text(runs_entry, '')


def create_script():
    """ Minimize app to task bar and start creation thread. """
    create_tool_tip.close()
    app.wm_state('iconic')
    mouse_script_name = script_name_entry.get()
    mouse_script_name = 'unnamed script' if mouse_script_name == '' else mouse_script_name
    mouse_script_name = generate_unique_mouse_script_name(mouse_script_name)
    result = start_recording(mouse_script_name)
    if result == SAVED:
        create_option_menu(mouse_script_name)
        set_text(script_name_entry, '')
        info_tool_tip = 'Used monitor setup: {}'.format(get_visual_setup())
        CreateToolTip(info_button, info_tool_tip)


# setup
app = Tk()
app.title('AutoClicker')
app.iconbitmap(ASSETS_DIR + 'icon.ico')
app.minsize(WIDTH, HEIGHT)
app.maxsize(WIDTH, HEIGHT)
main_frame = Frame(master=app, bd=2, relief='sunken')
main_frame.grid(row=0, column=0, rowspan=6, columnspan=10, sticky=NE, ipadx=5, padx=15)
dropdown_value = StringVar(master=main_frame)

# row 0
info_button = Button(main_frame, text='info')
info_button.grid_configure(row=0, column=2)
create_option_menu()

# row 1
Label(master=main_frame, text='runs').grid_configure(row=1, column=0, padx=5, pady=2)
runs_entry = Entry(master=main_frame)
runs_entry.grid_configure(row=1, column=1, padx=2, pady=2, columnspan=2)

# row 2
Label(master=main_frame, text='interval (in seconds)').grid_configure(row=2, column=0, padx=5, pady=2)
pause_duration_entry = Entry(master=main_frame)
pause_duration_entry.grid_configure(row=2, column=1, padx=2, pady=2, columnspan=2)

# row 3
start_button = Button(master=main_frame, text='start script',
                      command=lambda: start_script(dropdown_value.get()))
start_button.grid_configure(row=3, column=0)
start_tool_tip_txt = 'Click this button then press "{}" to start the script.\n Press "{}" at any time to stop it.' \
    .format(START_BUTTON.name, STOP_BUTTON.name)
start_tool_tip = CreateToolTip(start_button, start_tool_tip_txt)

delete_button = Button(master=main_frame, text='delete script',
                       command=lambda: delete_script(dropdown_value.get()))
delete_button.grid_configure(row=3, column=2)
delete_tool_tip = 'Delete selected script.'
CreateToolTip(delete_button, delete_tool_tip)

# row 4
Label(master=main_frame, text='name').grid_configure(row=4, column=0, padx=5, pady=2)

script_name_entry = Entry(master=main_frame)
script_name_entry.grid_configure(row=4, column=1, padx=5, pady=2, columnspan=5)

# row 5
new_script_button = Button(master=main_frame, text='create new script',
                           command=lambda: create_script())
new_script_button.grid_configure(row=5, column=0, padx=2, pady=2, columnspan=10)
create_tool_tip_txt = 'Click this button then press "{}" to start recording.\n Press "{}"' \
                      ' at any time to stop recording.'.format(START_BUTTON.name, STOP_BUTTON.name)
create_tool_tip = CreateToolTip(new_script_button, create_tool_tip_txt)


if __name__ == '__main__':
    setup()
    app.mainloop()
