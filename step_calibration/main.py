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
    results_path = os.path.join(os.path.dirname(__file__), filename)
    with open(results_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['block', 'trial', 'opacity', 'response', 'seen', 'coin_type', 'chosen_coin', 'correct', 'step'])
        writer.writeheader()
        for row in data:
            cleaned_row = {k: v if v is not None else '' for k, v in row.items()}
            writer.writerow(cleaned_row)

def show_message(win, message, wait_for_key=True):
    text = visual.TextStim(win, text=message, height=30, pos=(0, 0))
    text.draw()
    win.flip()
    if wait_for_key:
        event.waitKeys(keyList=['space', 'escape'])
        if 'escape' in event.getKeys():
            core.quit()

if __name__ == "__main__":
    config = load_config()
    calibration_config = load_calibration_config()
    num_blocks = calibration_config.get('num_blocks', 1)
    win = setup_window(config)
    arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS = setup_stimuli(win, config)
    
    all_data = []
    final_opacities = []
    for block in range(1, num_blocks + 1):
        show_message(win, f"Block {block} out of {num_blocks}\nReady to start? (Press space)", wait_for_key=True)
        print(f"Starting block {block}")
        data = run_calibration(win, arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS, config, calibration_config)
        for row in data:
            row['block'] = block
        all_data.extend(data)
        # Find final opacity
        for row in reversed(data):
            if row['trial'] == 'final':
                final_opacities.append(row['opacity'])
                break
        if 1 < block:
            show_message(win, "Good job!", wait_for_key=True)
    
    # Calculate overall final
    if final_opacities:
        overall_final = sum(final_opacities) / len(final_opacities)
        all_data.append({
            'block': 'overall',
            'trial': 'final',
            'opacity': overall_final,
            'response': '',
            'seen': '',
            'coin_type': '',
            'chosen_coin': '',
            'correct': '',
            'step': ''
        })
    
    save_data(all_data, 'calibration_results.csv')
    cleanup(win)