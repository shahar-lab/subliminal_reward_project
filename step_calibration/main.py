import random
import csv
import json
import os
from psychopy import visual, core, event
from calibration_logic import run_calibration

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path) as f:
        config = json.load(f)
    return config

def load_calibration_config():
    config_path = os.path.join(os.path.dirname(__file__), 'calibration_config.json')
    with open(config_path) as f:
        calibration_config = json.load(f)
    return calibration_config

def setup_window(config):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    WINDOW_COLOR = 'black'
    UNITS = 'pix'
    win = visual.Window(size=(WINDOW_WIDTH, WINDOW_HEIGHT), color=WINDOW_COLOR, units=UNITS)
    return win

def setup_stimuli(win, config):
    ARM_POSITIONS = [tuple(pos) for pos in config['arm_positions']]
    ARM_WIDTH = 100
    ARM_HEIGHT = 100
    ARM_COLOR = 'darkgray'
    CIRCLE_RADIUS = 30
    CIRCLE_INACTIVE_COLOR = 'gray'
    CIRCLE_ACTIVE_COLORS = ['red', 'blue', 'green', 'yellow']
    
    arms = []
    for pos in ARM_POSITIONS:
        arm = visual.Rect(win, width=ARM_WIDTH, height=ARM_HEIGHT, fillColor=ARM_COLOR, pos=pos)
        arms.append(arm)
    
    gray_circles = [visual.Circle(win, radius=CIRCLE_RADIUS, fillColor=CIRCLE_INACTIVE_COLOR, pos=pos) for pos in ARM_POSITIONS]
    colored_circles = [visual.Circle(win, radius=CIRCLE_RADIUS, fillColor=col, pos=pos) for col, pos in zip(CIRCLE_ACTIVE_COLORS, ARM_POSITIONS)]
    
    return arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS

def save_data(data, filename):
    results_path = os.path.join(os.path.dirname(__file__), '..', filename)
    with open(results_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['trial', 'opacity', 'response', 'seen', 'coin_type'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

def cleanup(win):
    win.close()

if __name__ == "__main__":
    config = load_config()
    calibration_config = load_calibration_config()
    win = setup_window(config)
    arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS = setup_stimuli(win, config)
    
    data = run_calibration(win, arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS, config, calibration_config)
    
    save_data(data, 'calibration_results.csv')
    cleanup(win)