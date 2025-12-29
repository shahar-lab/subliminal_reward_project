import random
import os
from psychopy import visual, core, event

def initialize_experiment(config, ARM_POSITIONS):
    initial_prob = config['initial_prob']
    step_size = config['step_size']
    coin_opacity = config['coin_opacity']
    time_limit = config['time_limit']
    n_rounds = config['n_rounds']
    
    probs = [initial_prob] * len(ARM_POSITIONS)
    data = []
    mouse = event.Mouse(win=None)  # Will set win later
    
    FEEDBACK_POS = (0, 200)
    TEXT_HEIGHT = 30
    INVALID_TRIAL_FEEDBACK_TEXT_COLOUR = 'red'
    SMALL_WAIT = 0.01
    MASK_DURATION = 0.333
    REWARD_DURATION = 0.033
    BLANK_DURATION = 0.033
    MASK_SHORT_DURATION = 0.033
    INVALID_TRIAL_MESSAGE_DURATION = 1.0
    
    return probs, data, mouse, initial_prob, step_size, coin_opacity, time_limit, n_rounds, FEEDBACK_POS, TEXT_HEIGHT, INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, SMALL_WAIT, MASK_DURATION, REWARD_DURATION, BLANK_DURATION, MASK_SHORT_DURATION, INVALID_TRIAL_MESSAGE_DURATION

def select_active_circles(ARM_POSITIONS, CIRCLE_ACTIVE_COLORS):
    active_indices = random.sample(range(len(ARM_POSITIONS)), 2)
    active_colors = random.sample(CIRCLE_ACTIVE_COLORS, 2)
    return active_indices, active_colors

def assign_colors_to_circles(colored_circles, active_indices, active_colors):
    for idx, i in enumerate(active_indices):
        colored_circles[i].fillColor = active_colors[idx]

def draw_initial_screen(win, arms, gray_circles, colored_circles, active_indices):
    for arm in arms:
        arm.draw()
    for circle in gray_circles:
        circle.draw()
    for i in active_indices:
        colored_circles[i].draw()
    win.flip()

def check_for_quit():
    keys = event.getKeys()
    return 'escape' in keys

def wait_for_choice(win, arms, mouse, time_limit, SMALL_WAIT):
    choice = None
    start_time = core.getTime()
    while choice is None:
        if check_for_quit():
            return None
        if mouse.getPressed()[0]:
            pos = mouse.getPos()
            for i, arm in enumerate(arms):
                if arm.contains(pos):
                    choice = i
                    break
        if time_limit > 0 and core.getTime() - start_time > time_limit:
            choice = -1
            break
        core.wait(SMALL_WAIT)
    return choice

def handle_timeout(win, arms, gray_circles, colored_circles, active_indices, FEEDBACK_POS, TEXT_HEIGHT, INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, INVALID_TRIAL_MESSAGE_DURATION):
    timeout_text = visual.TextStim(win, text="Too late!", pos=FEEDBACK_POS, color=INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, height=TEXT_HEIGHT)
    timeout_text.draw()
    for arm in arms:
        arm.draw()
    win.flip()
    core.wait(INVALID_TRIAL_MESSAGE_DURATION)
    
    draw_initial_screen(win, arms, gray_circles, colored_circles, active_indices)

def handle_invalid_choice(win, arms, gray_circles, colored_circles, active_indices, FEEDBACK_POS, TEXT_HEIGHT, INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, INVALID_TRIAL_MESSAGE_DURATION):
    invalid_text = visual.TextStim(win, text="Invalid choice", pos=FEEDBACK_POS, color=INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, height=TEXT_HEIGHT)
    invalid_text.draw()
    for arm in arms:
        arm.draw()
    for circle in gray_circles:
        circle.draw()
    for i in active_indices:
        colored_circles[i].draw()
    win.flip()
    core.wait(INVALID_TRIAL_MESSAGE_DURATION)
    
    draw_initial_screen(win, arms, gray_circles, colored_circles, active_indices)

def hide_circles(win, arms):
    for arm in arms:
        arm.draw()
    win.flip()
    core.wait(0.5)

def determine_reward(probs, choice):
    return random.random() < probs[choice]

def prepare_feedback(reward, coin_opacity, FEEDBACK_POS, win):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'stimuli')
    if reward:
        image_path = os.path.join(base_path, 'rewards', 'coin_reward.png')
    else:
        image_path = os.path.join(base_path, 'rewards', 'coin_no_reward.png')
    
    feedback = visual.ImageStim(win, image=image_path, pos=FEEDBACK_POS, opacity=coin_opacity)
    mask_path = os.path.join(base_path, 'masks', 'mask.png')
    mask = visual.ImageStim(win, image=mask_path, pos=FEEDBACK_POS)
    return feedback, mask

def show_feedback_sequence(win, arms, feedback, mask, MASK_DURATION, REWARD_DURATION, BLANK_DURATION, MASK_SHORT_DURATION):
    # Mask for 333 ms
    mask.draw()
    for arm in arms:
        arm.draw()
    win.flip()
    core.wait(MASK_DURATION)
    
    # Reward for 33 ms
    feedback.draw()
    for arm in arms:
        arm.draw()
    win.flip()
    core.wait(REWARD_DURATION)
    
    # Blank for 33 ms
    for arm in arms:
        arm.draw()
    win.flip()
    core.wait(BLANK_DURATION)
    
    # Mask for 33 ms
    mask.draw()
    for arm in arms:
        arm.draw()
    win.flip()
    core.wait(MASK_SHORT_DURATION)

def record_data(data, round_num, choice, reward, probs):
    data.append({
        'round': round_num,
        'choice': choice,
        'reward': int(reward),
        'probs': probs.copy()
    })

def update_probs(probs, step_size):
    for i in range(4):
        probs[i] += random.gauss(0, step_size)
        probs[i] = max(0, min(1, probs[i]))

def show_circles_again(win, arms, gray_circles, colored_circles, active_indices):
    for arm in arms:
        arm.draw()
    for circle in gray_circles:
        circle.draw()
    for i in active_indices:
        colored_circles[i].draw()
    win.flip()

def run_experiment(win, arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS, config):
    probs, data, mouse, initial_prob, step_size, coin_opacity, time_limit, n_rounds, FEEDBACK_POS, TEXT_HEIGHT, INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, SMALL_WAIT, MASK_DURATION, REWARD_DURATION, BLANK_DURATION, MASK_SHORT_DURATION, INVALID_TRIAL_MESSAGE_DURATION = initialize_experiment(config, ARM_POSITIONS)
    mouse.win = win  # Set win for mouse
    
    round_num = 0
    while round_num < n_rounds:
        round_num += 1
        
        active_indices, active_colors = select_active_circles(ARM_POSITIONS, CIRCLE_ACTIVE_COLORS)
        assign_colors_to_circles(colored_circles, active_indices, active_colors)
        draw_initial_screen(win, arms, gray_circles, colored_circles, active_indices)
        
        if check_for_quit():
            break
        
        choice = wait_for_choice(win, arms, mouse, time_limit, SMALL_WAIT)
        
        if choice is None:
            break
        
        if choice == -1:
            handle_timeout(win, arms, gray_circles, colored_circles, active_indices, FEEDBACK_POS, TEXT_HEIGHT, INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, INVALID_TRIAL_MESSAGE_DURATION)
            continue
        
        if choice not in active_indices:
            handle_invalid_choice(win, arms, gray_circles, colored_circles, active_indices, FEEDBACK_POS, TEXT_HEIGHT, INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, INVALID_TRIAL_MESSAGE_DURATION)
            continue
        
        hide_circles(win, arms)
        
        reward = determine_reward(probs, choice)
        
        feedback, mask = prepare_feedback(reward, coin_opacity, FEEDBACK_POS, win)
        
        show_feedback_sequence(win, arms, feedback, mask, MASK_DURATION, REWARD_DURATION, BLANK_DURATION, MASK_SHORT_DURATION)
        
        record_data(data, round_num, choice, reward, probs)
        
        update_probs(probs, step_size)
        
        show_circles_again(win, arms, gray_circles, colored_circles, active_indices)
    
    return data