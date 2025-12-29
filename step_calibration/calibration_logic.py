import random
import os
from psychopy import visual, core, event
import scipy.stats as stats

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
    text = "What did you see?\n" + "\n".join(response_options) + "\nPress 0-3 (or numpad 0-3)"
    question = visual.TextStim(win, text=text, height=TEXT_HEIGHT, pos=(0, 0))
    question.draw()
    win.flip()
    
    keys = event.waitKeys(keyList=['0', '1', '2', '3', 'num_0', 'num_1', 'num_2', 'num_3', 'escape'])
    if 'escape' in keys:
        return -1  # Signal to quit
    response_key = keys[0]
    if response_key.startswith('num_'):
        response = int(response_key[4:])  # 'num_0' -> 0
    else:
        response = int(response_key)
    return response

def discrimination_task(win, TEXT_HEIGHT, coin_type):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'stimuli', 'rewards')
    gold_coin = visual.ImageStim(win, image=os.path.join(base_path, 'coin_reward.png'), pos=(-100, 200))
    black_coin = visual.ImageStim(win, image=os.path.join(base_path, 'coin_no_reward.png'), pos=(100, 200))
    
    question = visual.TextStim(win, text="What did you most likely see?\nLeft Arrow: Gold Coin    Right Arrow: Black Coin\nPress Left or Right Arrow", height=TEXT_HEIGHT, pos=(0, 0))
    question.draw()
    gold_coin.draw()
    black_coin.draw()
    win.flip()
    
    keys = event.waitKeys(keyList=['left', 'right', 'escape'])
    if 'escape' in keys:
        return None, -1  # Signal to quit
    choice = keys[0]
    if choice == 'left':
        chosen_coin = 'gold'
    else:
        chosen_coin = 'black'
    
    correct = 1 if chosen_coin == coin_type else 0
    return chosen_coin, correct

def adjust_opacity(opacity, step, response, correct, min_opacity, max_opacity):
    if response == 0:  # Didn't see, increase opacity
        adj_dir = 1
    elif response >= 1 and correct == 0:  # Saw something but wrong coin, no change
        adj_dir = 0
    else:  # Saw something and correct, decrease opacity
        adj_dir = -1
    
    opacity += adj_dir * step
    opacity = max(min_opacity, min(max_opacity, opacity))
    return opacity, adj_dir

def run_calibration(win, arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS, config, calibration_config):
    response_options = calibration_config['response_options']
    coin_probability = calibration_config['coin_probability']
    initial_step = calibration_config['initial_step']
    step_decrease = calibration_config['step_decrease']
    min_step = calibration_config['min_step']
    min_opacity = calibration_config.get('min_opacity', 0.1)
    max_opacity = calibration_config.get('max_opacity', 1.0)
    cwir_stop = calibration_config.get('cwir_stop', 50)
    initial_opacity, _, _, _, _, max_trials, min_trials, max_reversals, data, mouse, FEEDBACK_POS, TEXT_HEIGHT, SMALL_WAIT, REWARD_DURATION, MASK_DURATION, BLANK_DURATION = initialize_calibration(config)
    
    opacity = initial_opacity
    step = initial_step
    trial = 1
    reversals = 0
    prev_adj_dir = 0
    total_cwir = 0
    streak = 0
    responses = []
    corrects = []
    series_opacities = []
    series_cwirs = []
    current_series_opacities = []
    
    while True:
        # Show arms
        draw_arms(win, arms, gray_circles)
        core.wait(0.333)  # Wait for fixation
        
        # Prepare stimuli
        coin, coin_type = prepare_coin(win, opacity, FEEDBACK_POS, coin_probability)
        mask = prepare_mask(win, FEEDBACK_POS)
        
        # Append current opacity to series
        current_series_opacities.append(opacity)
        
        # Show stimulus sequence
        show_stimulus(win, coin, mask, arms, gray_circles, REWARD_DURATION, MASK_DURATION, BLANK_DURATION)
        
        # Get response
        response = get_response(win, TEXT_HEIGHT, response_options)
        if response == -1:
            break
        
        # Discrimination task
        chosen_coin, correct = discrimination_task(win, TEXT_HEIGHT, coin_type)
        if correct == -1:
            break
        
        # Append to lists
        responses.append(response)
        corrects.append(correct)
        
        # Update cwir
        if correct == 0:
            streak += 1
        else:
            if streak > 0:
                cwir_series = streak * (streak + 1) // 2
                total_cwir += cwir_series
                avg_opacity = sum(current_series_opacities) / len(current_series_opacities)
                series_opacities.append(avg_opacity)
                series_cwirs.append(cwir_series)
                current_series_opacities = []
                streak = 0
        
        # Adjust opacity
        new_opacity, adj_dir = adjust_opacity(opacity, step, response, correct, min_opacity, max_opacity)
        
        # Update step size if adjustment was made
        if adj_dir != 0:
            step = max(min_step, step - step_decrease)
        
        if adj_dir != prev_adj_dir and prev_adj_dir != 0:
            reversals += 1
        
        prev_adj_dir = adj_dir
        opacity = new_opacity
        
        # Update max_opacity if discrimination performance is significant
        if len(corrects) > 0:
            seen_ratio = sum(1 for r in responses if r >= 1) / len(responses)
            criterion = 0.05 / (total_cwir + 1)
            binom_result = stats.binomtest(sum(corrects), len(corrects), p=0.5, alternative='two-sided')
            if binom_result.pvalue < criterion:
                max_opacity = (1 - seen_ratio) * max_opacity + seen_ratio * opacity
        
        # Check end condition
        if total_cwir >= cwir_stop:
            break
        
        # Record data
        data.append({
            'trial': trial,
            'opacity': opacity,
            'response': response,
            'seen': 1 if response > 0 else 0,
            'coin_type': coin_type,
            'chosen_coin': chosen_coin,
            'correct': correct,
            'step': step
        })
        
        trial += 1
        
        # Check for quit
        if event.getKeys(keyList=['escape']):
            break
    
    # Calculate final opacity
    if total_cwir > 0:
        final_opacity = sum(c * a for c, a in zip(series_cwirs, series_opacities)) / total_cwir
        data.append({
            'trial': 'final',
            'opacity': final_opacity,
            'response': None,
            'seen': None,
            'coin_type': None,
            'chosen_coin': None,
            'correct': None,
            'step': None
        })
    
    return data