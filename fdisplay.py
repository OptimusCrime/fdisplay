#!/usr/bin/python3

import os
import subprocess
import re
import sys

def get_displayplacer_data():
    process = subprocess.Popen(['displayplacer', 'list'], user=os.getlogin(), stdout=subprocess.PIPE)
    stdout, _ = process.communicate()
    process.kill()

    return [x.decode('utf-8').strip() for x in stdout.splitlines()]


def run_displayplacer_command(command):
    process = subprocess.Popen('displayplacer ' + command, user=os.getlogin(), stdout=subprocess.PIPE, shell=True)
    stdout, _ = process.communicate()
    process.kill()


def get_screen_id(data, index):
    line = data[index - 3].split(':')
    return line[1].strip()


def find_display_ids(data):
    screens = {
        'main': '',
        'external': []
    }

    for index, line in enumerate(data):
        lower_line = line.lower()

        if 'macbook built in' in lower_line:
            screens['main'] = get_screen_id(data, index)

        if 'external' in lower_line:
            screens['external'].append(get_screen_id(data, index))

    return screens


def convert_to_output(screens):
    output = []
    for screen in screens:
        line = '\"' + (' '.join('{}:{}'.format(key, value) for key, value in screen.items())) + '\"'
        output.append(line)
    return ' '.join(output)


def parse_output(text):
    screens_text = re.findall('"[^"]+"', text)

    screens = []
    for screen_text in screens_text:
        screen_text = screen_text.replace('"', "").split(" ")

        screen = {}

        for screen_attribute in screen_text:
            split = screen_attribute.split(':')

            if len(split) != 2:
                continue

            screen[split[0]] = split[1]

        screens.append(screen)
    return screens


def get_resolution_width(display):
    res = display['res'].split('x')
    return int(res[0])


def get_origin(display):
    origin = display['origin'].split(',')
    return int(origin[0].replace('(', ''))


def reorder_displays(displays, display_ids, orientation):
    externals = [display for display in displays if display['id'] in display_ids['external']]

    d = {
        'macbook': next(display for display in displays if display['id'] == display_ids['main']),
        'external_1': externals[0],
        'external_2': externals[1] if len(externals) > 1 else None
    }

    if d['external_2'] is not None:
        # Not sure if this will work or not, but we'll use the external display with the highest origin as
        # number 1. This should make the screens swap position every time the script runs
        origin_1 = get_origin(d['external_1'])
        origin_2 = get_origin(d['external_2'])

        if origin_1 > origin_2:
            d['external_1'], d['external_2'] = d['external_2'], d['external_1']

    # If macbook is on the left, then the macbook screen should have a negative origin
    origin_multiplier = -1 if orientation == 'left' else 1

    # The external display should always be (0,0)
    d['external_1']['origin'] = '(0,0)'

    # The macbook display should be minus the width resolution of the external display
    width = get_resolution_width(d['external_1'])

    if d['external_2'] is not None:
        d['external_2']['origin'] = '(' + str(width * origin_multiplier) + ',0)'
        width += get_resolution_width(d['external_2'])

    d['macbook']['origin'] = '(' + str(width * origin_multiplier) + ',0)'

    res = [
        d['macbook'],
        d['external_1']
    ]

    if d['external_2'] is not None:
        res.append(d['external_2'])

    return res


def get_command_output(displays, display_ids, orientation):
    reordered_displays = reorder_displays(displays[:], display_ids, orientation)
    return convert_to_output(reordered_displays)


def get_macbook_orientation():
    args = sys.argv

    if len(args) != 2:
        return 'left'

    if args[1] == 'left' or args[1] == 'right':
        return args[1]

    return 'left'


def main():
    orientation = get_macbook_orientation()
    data = get_displayplacer_data()
    display_ids = find_display_ids(data)

    # The last line contains the formatted output
    displays = parse_output(data[-1])

    if len(displays) != 2 and len(displays) != 3:
        print('Script only support one or two external monitors')
        return

    command_output = get_command_output(displays[:], display_ids, orientation)
    run_displayplacer_command(command_output)


if __name__ == '__main__':
    main()
