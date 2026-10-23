import random
import os
from psychopy import visual, core, event

def initialize_experiment(config, ARM_POSITIONS, win):
    initial_prob = config['initial_prob']
    step_size = config['step_size']
    coin_opacity = config['coin_opacity']
    n_rounds = config['n_rounds']
    
    probs = [initial_prob] * len(ARM_POSITIONS)
    data = []
    
    # --- VISUAL CONSTANTS ---
    FEEDBACK_POS = (0, 200) # Position of top square/feedback
    TEXT_HEIGHT = 30
    INVALID_TRIAL_FEEDBACK_TEXT_COLOUR = 'red'
    INACTIVE_CIRCLE_COLOR = 'gray' # Color for the unchoosable circles
    
    # Size for the top gray square (should match your arm size)
    SQUARE_SIZE = (100, 100) 
    
    # Size for mask/coin (should match your colored circles)
    STIM_SIZE = (80, 80) 
    
    # Create the background square for the top feedback area
    top_bkg_square = visual.Rect(
        win=win,
        pos=FEEDBACK_POS,
        size=SQUARE_SIZE,
        fillColor='darkgray',
        opacity=1.0
    )

    # --- TIMING CONSTANTS (Seconds) ---
    TIME_LIMIT = 6.0            # Time to choose
    WAIT_INITIAL = 1.0          # Empty squares before circles appear
    WAIT_POST_CHOICE = 1.0      # Empty squares after choice, before mask
    MASK_DURATION_LONG = 1.0    # First mask
    REWARD_DURATION = 3 # 0.033     # Reward/No-reward presentation
    MASK_DURATION_SHORT = 0.033 # Second mask
    INVALID_MSG_DURATION = 1.0
    SMALL_WAIT = 0.01

    # --- INPUT CONSTANTS ---
    # Map keys s, f, h, k to indices 0, 1, 2, 3
    KEY_MAP = {'s': 0, 'f': 1, 'h': 2, 'k': 3} 

    return (probs, data, initial_prob, step_size, coin_opacity, n_rounds, 
            FEEDBACK_POS, TEXT_HEIGHT, INVALID_TRIAL_FEEDBACK_TEXT_COLOUR, 
            INACTIVE_CIRCLE_COLOR, top_bkg_square, STIM_SIZE,
            TIME_LIMIT, WAIT_INITIAL, WAIT_POST_CHOICE, 
            MASK_DURATION_LONG, REWARD_DURATION, MASK_DURATION_SHORT, 
            INVALID_MSG_DURATION, SMALL_WAIT, KEY_MAP)

def select_active_circles(ARM_POSITIONS, CIRCLE_ACTIVE_COLORS):
    active_indices = random.sample(range(len(ARM_POSITIONS)), 2)
    active_colors = random.sample(CIRCLE_ACTIVE_COLORS, 2)
    return active_indices, active_colors

def assign_colors_to_circles(colored_circles, active_indices, active_colors, INACTIVE_COLOR):
    """
    Assigns active colors to chosen indices and Dark Gray to the others.
    """
    # Create a dictionary mapping index -> color for the active ones
    active_map = dict(zip(active_indices, active_colors))
    
    for i in range(len(colored_circles)):
        if i in active_indices:
            # It's an active circle
            colored_circles[i].fillColor = active_map[i]
            # Ideally keep lineColor consistent or same as fill
            colored_circles[i].lineColor = active_map[i] 
        else:
            # It's an inactive circle
            colored_circles[i].fillColor = INACTIVE_COLOR
            colored_circles[i].lineColor = INACTIVE_COLOR 

def draw_background_only(win, arms, top_bkg_square):
    """Draws the 4 bottom squares and the 1 top square."""
    for arm in arms:
        arm.draw()
    top_bkg_square.draw()
    win.flip()

def draw_stimuli_screen(win, arms, top_bkg_square, colored_circles):
    """Draws background squares + ALL 4 circles (2 colored, 2 dark gray)."""
    for arm in arms:
        arm.draw()
    top_bkg_square.draw()
    
    # Draw all circles. assign_colors_to_circles handled the coloring.
    for circle in colored_circles:
        circle.draw()
        
    win.flip()

def check_for_quit():
    keys = event.getKeys()
    return 'escape' in keys

def wait_for_choice(win, arms, top_bkg_square, time_limit, SMALL_WAIT, KEY_MAP):
    choice = None
    start_time = core.getTime()
    event.clearEvents() 
    
    while choice is None:
        keys = event.getKeys()
        
        if 'escape' in keys:
            return None
        
        for key in keys:
            if key in KEY_MAP:
                choice = KEY_MAP[key]
                break
        
        if time_limit > 0 and core.getTime() - start_time > time_limit:
            choice = -1 
            break
            
        core.wait(SMALL_WAIT)
    return choice

def handle_timeout(win, arms, top_bkg_square, FEEDBACK_POS, TEXT_HEIGHT, INVALID_COLOUR, DURATION):
    timeout_text = visual.TextStim(win, text="Too late!", pos=FEEDBACK_POS, color=INVALID_COLOUR, height=TEXT_HEIGHT)
    
    for arm in arms:
        arm.draw()
    top_bkg_square.draw()
    timeout_text.draw()
    win.flip()
    core.wait(DURATION)

def handle_invalid_choice(win, arms, top_bkg_square, FEEDBACK_POS, TEXT_HEIGHT, INVALID_COLOUR, DURATION):
    invalid_text = visual.TextStim(win, text="Invalid choice", pos=FEEDBACK_POS, color=INVALID_COLOUR, height=TEXT_HEIGHT)
    
    for arm in arms:
        arm.draw()
    top_bkg_square.draw()
    invalid_text.draw()
    win.flip()
    core.wait(DURATION)

def determine_reward(probs, choice):
    return random.random() < probs[choice]

def prepare_feedback(reward, coin_opacity, FEEDBACK_POS, STIM_SIZE, win):
    base_path = os.path.join(os.path.dirname(__file__), '..', 'stimuli')
    
    if reward:
        image_path = os.path.join(base_path, 'rewards', 'coin_reward.png')
    else:
        image_path = os.path.join(base_path, 'rewards', 'coin_no_reward.png')
    
    feedback = visual.ImageStim(win, image=image_path, pos=FEEDBACK_POS, opacity=coin_opacity, size=STIM_SIZE)
    mask_path = os.path.join(base_path, 'masks', 'mask.png')
    mask = visual.ImageStim(win, image=mask_path, pos=FEEDBACK_POS, size=STIM_SIZE)
    
    return feedback, mask

def show_feedback_sequence(win, arms, top_bkg_square, feedback, mask, 
                           MASK_LONG, REWARD_DUR, MASK_SHORT):
    
    # 1. Mask for 1 second (Long)
    for arm in arms:
        arm.draw()
    top_bkg_square.draw() 
    mask.draw()           
    win.flip()
    core.wait(MASK_LONG)
    
    # 2. Reward/No Reward for 33 ms
    for arm in arms:
        arm.draw()
    top_bkg_square.draw()
    feedback.draw()
    win.flip()
    core.wait(REWARD_DUR)
    
    # 3. Mask for 33 ms (Short)
    for arm in arms:
        arm.draw()
    top_bkg_square.draw()
    mask.draw()
    win.flip()
    core.wait(MASK_SHORT)

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

def run_experiment(win, arms, gray_circles, colored_circles, ARM_POSITIONS, CIRCLE_ACTIVE_COLORS, config):
    # Unpack updated constants
    (probs, data, initial_prob, step_size, coin_opacity, n_rounds, 
     FEEDBACK_POS, TEXT_HEIGHT, INVALID_COLOUR, 
     INACTIVE_CIRCLE_COLOR, top_bkg_square, STIM_SIZE,
     TIME_LIMIT, WAIT_INITIAL, WAIT_POST_CHOICE, 
     MASK_LONG, REWARD_DUR, MASK_SHORT, 
     INVALID_MSG_DUR, SMALL_WAIT, KEY_MAP) = initialize_experiment(config, ARM_POSITIONS, win)
    
    round_num = 0
    while round_num < n_rounds:
        round_num += 1
        
        # 1. Setup Phase
        active_indices, active_colors = select_active_circles(ARM_POSITIONS, CIRCLE_ACTIVE_COLORS)
        
        # Apply colors: Active get color, Inactive get Dark Gray
        assign_colors_to_circles(colored_circles, active_indices, active_colors, INACTIVE_CIRCLE_COLOR)
        
        # 2. Initial Wait: Show empty gray squares (arms + top) for 1 second
        draw_background_only(win, arms, top_bkg_square)
        core.wait(WAIT_INITIAL)
        
        if check_for_quit(): break
        
        # 3. Stimuli Phase: Show colored circles + dark gray circles, wait for key
        draw_stimuli_screen(win, arms, top_bkg_square, colored_circles)
        
        choice = wait_for_choice(win, arms, top_bkg_square, TIME_LIMIT, SMALL_WAIT, KEY_MAP)
        
        if choice is None: # Escape pressed
            break
        
        if choice == -1: # Timeout
            handle_timeout(win, arms, top_bkg_square, FEEDBACK_POS, TEXT_HEIGHT, INVALID_COLOUR, INVALID_MSG_DUR)
            continue
        
        if choice not in active_indices: # Invalid Key (chose a dark gray circle)
            handle_invalid_choice(win, arms, top_bkg_square, FEEDBACK_POS, TEXT_HEIGHT, INVALID_COLOUR, INVALID_MSG_DUR)
            continue
        
        # 4. Post-Choice Phase: Hide circles, show empty squares for 1 second
        draw_background_only(win, arms, top_bkg_square)
        core.wait(WAIT_POST_CHOICE)
        
        # 5. Feedback Phase
        reward = determine_reward(probs, choice)
        feedback, mask = prepare_feedback(reward, coin_opacity, FEEDBACK_POS, STIM_SIZE, win)
        
        show_feedback_sequence(win, arms, top_bkg_square, feedback, mask, 
                               MASK_LONG, REWARD_DUR, MASK_SHORT)
        
        # 6. Data & Updates
        record_data(data, round_num, choice, reward, probs)
        update_probs(probs, step_size)
    
    return data