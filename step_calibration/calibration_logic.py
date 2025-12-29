import random
import os
from psychopy import visual, core, event
import numpy as np

def initialize_calibration(config):
    initial_opacity = 1.0
    min_opacity = 0.1
    max_opacity = 1.0
    initial_step = 0.1
    min_step = 0.01
    max_trials = 100
    min_trials = 50
    max_reversals = 20
    
    data = []
    mouse = event.Mouse(win=None)
    
    FEEDBACK_POS = (0, 200)
    TEXT_HEIGHT = 30
    SMALL_WAIT = 0.01
    REWARD_DURATION = 0.033
    MASK_DURATION = 0.333
    BLANK_DURATION = 0.033
    
    return initial_opacity, min_opacity, max_opacity, initial_step, min_step, max_trials, min_trials, max_reversals, data, mouse, FEEDBACK_POS, TEXT_HEIGHT, SMALL_WAIT, REWARD_DURATION, MASK_DURATION, BLANK_DURATION

def prepare_coin(win, opacity, FEEDBACK_POS, coin_probability):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'stimuli')
    if random.random() < coin_probability:
        image_path = os.path.join(base_path, 'rewards', 'coin_reward.png')  # gold
        coin_type = 'gold'
    else:
        image_path = os.path.join(base_path, 'rewards', 'coin_no_reward.png')  # black
        coin_type = 'black'
    coin = visual.ImageStim(win, image=image_path, pos=FEEDBACK_POS, opacity=opacity)
    return coin, coin_type

def prepare_mask(win, FEEDBACK_POS):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'stimuli')
    mask_path = os.path.join(base_path, 'masks', 'mask.png')
    mask = visual.ImageStim(win, image=mask_path, pos=FEEDBACK_POS)
    return mask

def draw_arms(win, arms, gray_circles):
    for arm in arms:
        arm.draw()
    for circle in gray_circles:
        circle.draw()
    win.flip()

def show_stimulus(win, coin, mask, arms, gray_circles, REWARD_DURATION, MASK_DURATION, BLANK_DURATION):
    # Show coin with arms
    for arm in arms:
        arm.draw()
    for circle in gray_circles:
        circle.draw()
    coin.draw()
    win.flip()
    core.wait(REWARD_DURATION)
    
    # Show mask with arms
    for arm in arms:
        arm.draw()
    for circle in gray_circles:
        circle.draw()
    mask.draw()
    win.flip()
    core.wait(MASK_DURATION)
    
    # Blank with arms
    for arm in arms:
        arm.draw()
    for circle in gray_circles:
        circle.draw()
    win.flip()
    core.wait(BLANK_DURATION)

def get_response(win, TEXT_HEIGHT, response_options):
    text = "What did you see?\n" + "\n".join(response_options) + "\nPress 0-3"
    question = visual.TextStim(win, text=text, height=TEXT_HEIGHT, pos=(0, 0))
    question.draw()
    win.flip()
    
    keys = event.waitKeys(keyList=['0', '1', '2', '3', 'escape'])
    if 'escape' in keys:
        core.quit()
    response = int(keys[0])
    return response

def adjust_opacity(opacity, step, response, min_opacity, max_opacity):
    if response == 0:  # Saw nothing, increase opacity
        adj_dir = 1
    else:  # Saw something, decrease opacity
        adj_dir = -1
    
    opacity += adj_dir * step
    opacity = max(min_opacity, min(max_opacity, opacity))
    return opacity, adj_dir

def run_calibration(win, arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS, config, calibration_config):
    response_options = calibration_config['response_options']
    coin_probability = calibration_config['coin_probability']
    initial_opacity, min_opacity, max_opacity, initial_step, min_step, max_trials, min_trials, max_reversals, data, mouse, FEEDBACK_POS, TEXT_HEIGHT, SMALL_WAIT, REWARD_DURATION, MASK_DURATION, BLANK_DURATION = initialize_calibration(config)
    
    opacity = initial_opacity
    trial = 1
    reversals = 0
    prev_adj_dir = 0
    
    while trial <= max_trials and (trial <= min_trials or reversals < max_reversals):
        # Show arms
        draw_arms(win, arms, gray_circles)
        core.wait(1.0)  # Wait for fixation
        
        # Prepare stimuli
        coin, coin_type = prepare_coin(win, opacity, FEEDBACK_POS, coin_probability)
        mask = prepare_mask(win, FEEDBACK_POS)
        
        # Show stimulus sequence
        show_stimulus(win, coin, mask, arms, gray_circles, REWARD_DURATION, MASK_DURATION, BLANK_DURATION)
        
        # Get response
        response = get_response(win, TEXT_HEIGHT, response_options)
        
        # Adjust opacity
        step = max(min_step, initial_step - (initial_step - min_step) * (trial - 1) / max_trials)
        new_opacity, adj_dir = adjust_opacity(opacity, step, response, min_opacity, max_opacity)
        
        if adj_dir != prev_adj_dir and prev_adj_dir != 0:
            reversals += 1
        
        prev_adj_dir = adj_dir
        opacity = new_opacity
        
        # Record data
        data.append({
            'trial': trial,
            'opacity': opacity,
            'response': response,
            'seen': 1 if response > 0 else 0,
            'coin_type': coin_type
        })
        
        trial += 1
        
        # Check for quit
        if event.getKeys(keyList=['escape']):
            break
    
    return data