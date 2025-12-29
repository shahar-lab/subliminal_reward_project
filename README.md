# 4-Armed Bandit Task Experiment

This is a PsychoPy-based experiment implementing a 4-armed bandit task where participants choose between four colored squares (arms) to maximize rewards. The reward probabilities for each arm change each round in a random walk manner.

## Features

- 4 arms represented as colored squares: red, blue, green, yellow (2 active per round, 2 inactive shown as gray)
- Reward probabilities start at a constant value and change via random walk each round
- Mouse-based interaction for selecting arms
- Feedback display after each choice
- Data logging of choices, rewards, and current probabilities

## Configuration

Edit `config.json` to set:
- `initial_prob`: Starting reward probability for each arm (e.g., 0.5)
- `step_size`: Standard deviation of the random walk step (e.g., 0.05)

## Requirements

- Python 3.x
- PsychoPy library

## Installation

1. Install Python if not already installed.
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Experiment

Run the experiment using:
```
python main.py
```

The experiment will run for 50 rounds. In each round:
1. Four gray squares appear with 2 colored circles on top (active arms).
2. Click on an active colored circle to choose an arm.
3. Receive feedback on whether you got a reward.
4. Probabilities update via random walk.
5. Circles reappear for the next round.

## Output

Results are saved to `results.csv` with columns:
- round: The round number
- choice: The index of the chosen arm (0-3)
- reward: 1 if reward received, 0 otherwise
- probs: The current reward probabilities for all arms as a list

## Customization

You can modify parameters in `main.py`:
- `n_rounds`: Number of rounds (default: 50)

Or edit `config.json` for probabilities.