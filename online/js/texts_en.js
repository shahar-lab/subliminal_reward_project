// ─── texts_en.js ──────────────────────────────────────────────────────────────
// All participant-facing text, ENGLISH. Translated by Claude from the Hebrew lab texts
// (../texts/*.py); WM, IMI and final questions follow ioc-wm's English originals.
// The Hebrew version (texts_he.js) has exactly the same keys.
//
// Text format: '\n' = line break, '\n\n' = new paragraph (converted by para() in common.js).
// Placeholders in {braces} are filled in by the code from CONFIG.
// Page keys used by the code: reward_coin, no_reward_coin, mask, offer: [arms], scene, coins,
// fixation, example_memory, example_same, example_diff.

var TEXTS_EN = {
    dir: 'ltr',
    common: {
        NEXT: 'Next', PREV: 'Previous',
        NAV_HINT: 'Navigate with the arrow keys (&rarr; next, &larr; previous) or the buttons below.',
        QUIZ_SUBMIT: 'Submit answers',
        QUIZ_PREAMBLE: 'Please answer all questions to confirm you understood the instructions.',
        QUIZ_FAILED: 'You made a mistake in one or more of the questions.\n'
                   + 'We will now go back to the instructions - please read them again carefully and then answer the questions again.',
        BACK_TO_INSTRUCTIONS: 'Back to instructions',
        PRESS_SPACE: 'Press the space bar to continue',
        BREAK: 'Break.\nTake as long as you need.\n\nWhen you are ready, press the space bar to continue.',
        MOBILE_TITLE: 'This study requires a desktop or laptop computer.',
        MOBILE_TEXT: 'You appear to be using a mobile phone or tablet.\nUnfortunately you cannot take part on this device.\n'
                   + 'Please return this study on Prolific and come back when you have access to a desktop or laptop.',
        MOBILE_BUTTON: 'Return to Prolific',
        CAPTCHA: 'Please complete the CAPTCHA to proceed.', CAPTCHA_SUBMIT: 'Submit', CAPTCHA_ALERT: 'Please complete the CAPTCHA.',
        FULLSCREEN: 'This experiment runs in fullscreen mode.\n'
                  + 'Please make sure your browser is on 100% zoom, close other programs and tabs, and silence notifications.\n'
                  + 'Please sit comfortably at arm\'s length from the screen and keep your eyes on the screen throughout.',
        FULLSCREEN_BUTTON: 'Press here to enter fullscreen mode',
        PAUSE_ALERT: 'The experiment is paused. If necessary, please return to fullscreen by pressing F11. '
                   + 'Please stay fully engaged with the experiment until it ends.',
        WELCOME_DAY1: 'Welcome, and thank you for taking part!\n\n'
                    + 'This study has two parts, on two separate days: today and tomorrow. '
                    + 'You will receive an invitation to the second part after completing today\'s part. '
                    + 'Please take part only if you can complete both parts.\n\n'
                    + 'Today you will play two games: a "squares game" and a "casino game", and then answer a few questions.\n'
                    + 'Please stay attentive and in fullscreen mode throughout.',
        WELCOME_DAY2: 'Welcome back, and thank you for taking part in the second part of the study!\n\n'
                    + 'Today there is a short coin task, then the casino game you played yesterday, and then a few questions.\n'
                    + 'Please stay attentive and in fullscreen mode throughout.',
        WELCOME_CONTINUE: 'Press the space bar to continue.',
        DAY_END: 'You have finished today\'s part.\nThank you very much!',
        UPLOADING: 'Please wait a moment while your data are being saved...',
        REDIRECT: 'Please wait. You will be redirected back to Prolific in a few moments.\n\n'
                + 'If you get a pop-up warning that "data may not be saved", you can click "leave" - your data have already been saved.',
        REDIRECT_LINK: 'If you are not redirected automatically, please click here:',
        THANK_YOU_END: 'Thank you! You may now close this window.',
        DAY_STOPPED: 'This part of the study has ended.\nThank you for your participation.',
        DAY_STOPPED_BUTTON: 'Return to Prolific',
        REFRESH_MEASURING: 'Preparing the experiment, please wait...',
    },

    awareness: {
        PAS_QUESTION: 'How well did you see the coin?',
        PAS_OPTIONS: ['I saw nothing', 'I saw a vague flash, I don\'t know what it was',
                      'I saw the coin almost clearly', 'I saw the coin clearly'],
        PAS_FOOTER: 'Answer with the number keys 0-3',
        CHOICE_QUESTION: 'Which coin did you see?\nIf you did not see it - guess by your gut feeling.',
        CHOICE_FOOTER: 'Choose with the left or right arrow key',
    },

    bandit: {
        TITLE: 'The casino game',
        TITLE_DAY2: 'The subliminal casino game',
        PAGES_DAY1_INTRO: [
            { text: 'Welcome to the casino game!\n\n'
                  + 'We will now present the game instructions. Please read them carefully.\n'
                  + 'At the end of the instructions you will be asked a few short questions to make sure everything is clear.' },
        ],
        PAGES_DAY2_INTRO: [
            { text: 'Welcome to the subliminal casino game!\n\n'
                  + 'The instructions are the same as in the game you played yesterday, except that this time the prize '
                  + 'the casino machine gives you will be subliminal - that is, it will appear for a very short time.\n'
                  + 'Still, do your best to learn the locations and collect as many gold coins as possible!' },
        ],
        PAGES_RULES: [
            { text: 'During the game you make choices to try to win gold coins.\n'
                  + 'On each step you can get one gold coin, which looks like this:', reward_coin: true },
            { text: 'or get no coin. In that case, the following coin is shown:', no_reward_coin: true },
            { text: 'The game has four locations, and each one gives a coin with a different chance when you choose it.\n\n'
                  + 'To choose, press one of four keys: S F H K.\n'
                  + 'The keys match the locations on the screen: S chooses the leftmost location, F the second from the left, and so on.',
              offer: [0, 1, 2, 3] },
            { text: 'On each round, the casino machine randomly offers two locations to choose from, and marks them with a coloured circle.\n'
                  + 'Locations with a grey circle are not available.\n\n'
                  + 'Example: here you can choose only with the keys S and K.', offer: [0, 3] },
            { text: 'Another example: here you can choose only with the keys H and K.\n\n'
                  + 'Choose one of the offered locations by pressing its key. Right after your choice you will see whether you won a coin.',
              offer: [2, 3] },
        ],
        PAGE_MASK_DAY2: { text: 'This time, right before and right after the coin, the following picture will appear - '
                              + 'which will make it hard for you to see the coin.\n'
                              + 'Most likely you will not see the coin, but try to learn as best you can and collect as many gold coins as possible!',
                          mask: true },
        PAGES_TIPS: [
            { text: 'Note!\n\n'
                  + 'Each location has its own chance of giving a gold coin. The chances change slowly during the game, '
                  + 'like prices in a market that go up and down - so keep learning all the time.\n\n'
                  + 'Each location works differently: some may win more often, some less, or they may be similar. '
                  + 'You can learn about a location only by choosing it.' },
            { text: 'Only the location you chose determines whether you get a coin - not the colour of the circle inside it. '
                  + 'The coloured circles are there only to mark the two available locations.\n\n'
                  + 'You have {time_limit} seconds to choose a location. If you do not choose in time, a message will appear and you will move '
                  + 'on to the next round with no coin and no chance to learn from that round.\n'
                  + 'Choosing a location with a grey circle will show the message "Choice not available!" and delay you for {penalty} seconds, with no coin.' },
            { text: 'At the end of the game, the gold coins you collected will be counted. Your goal is to choose the right machines '
                  + 'to collect as many gold coins as possible!\n\n'
                  + 'The game has {n_trials} choices, with {n_breaks} breaks. Remember: the goal is to win as many coins as possible.' },
            { text: 'We will now ask you a few questions to make sure the instructions are clear.\n'
                  + 'If you want to go over the instructions again, go back now with the left arrow key.' },
        ],
        PROBE_SENTENCE: '\n\nOn some rounds you will be asked at the end of the round how well you saw the coin and which coin you think appeared. '
                      + 'Answer by your gut feeling.',
        QUIZ: [
            { name: 'n_locations', prompt: 'How many locations are there in the game in total?', options: ['2', '4', '6'], correct: 1 },
            { name: 'n_available', prompt: 'How many locations can be chosen each time?', options: ['2', '4', '6'], correct: 0 },
            { name: 'leftmost_key', prompt: 'How do you choose the leftmost location?', options: ['S', 'F', 'H', 'K'], correct: 0 },
            { name: 'middle_right_key', prompt: 'How do you choose the middle-right location?', options: ['S', 'F', 'H', 'K'], correct: 2 },
            { name: 'goal', prompt: 'What is the goal of the game?',
              options: ['To make the best choices and collect as many gold coins as possible', 'To choose the coloured circles as fast as possible'],
              correct: 0 },
            { name: 'colour', prompt: 'Does the colour of the circle affect the chance of winning a coin?',
              options: ['Yes, some colours win more', 'No, only the location determines the chance of winning'], correct: 1 },
            { name: 'changing_odds', prompt: 'Are the chances of winning of each location fixed throughout the game?',
              options: ['Yes, they do not change', 'No, they change slowly during the game'], correct: 1 },
            { name: 'time_limit', prompt: 'How much time do you have to choose a location on each round?',
              options: ['2 seconds', '{time_limit} seconds', 'There is no time limit'], correct: 1 },
        ],
        PRACTICE_START: 'Excellent!\nNow {n} practice rounds will start, to get to know the game.\nCoins in the practice are not counted.\n\nPress the space bar to start.',
        PRACTICE_END: 'The practice is over.\nNow the game itself will start. Good luck!\n\nPress the space bar to start.',
        TOO_LATE: 'No location chosen in time',
        UNAVAILABLE: 'Choice not available!',
        BREAK: 'You have finished {done} of {total} parts - break.\nTake as long as you need.\n\nWhen you are ready, press the space bar.',
        END_WITH_TOTAL: 'The game is over!\n\nYou collected {coins} gold coins.\n\nPress the space bar to continue.',
        END_NO_TOTAL: 'The game is over!\nThank you very much.\n\nPress the space bar to continue.',
    },

    calibration: {
        TITLE: 'Calibration',
        PAGES: [
            { text: 'Welcome, and thank you for taking part!\n\n'
                  + 'In this task you will be asked to look at a coin that appears for a very short time, and to report how well you saw it.' },
            { text: 'The coin will appear in the upper square on the screen, above the four grey squares - just like in the casino game you played yesterday.\n'
                  + 'In this part you do not need to choose a location. Ignore the squares in the row, and attend only to the coin.',
              scene: true },
            { text: 'The coin will be gold (right) or black (left):', coins: true },
            { text: 'The coin will appear for a very short time. Right before and right after it, a black-and-white picture '
                  + 'that looks like this will appear in the square:\n\n'
                  + 'The short presentation and the black-and-white picture are meant to make the coin hard to see.', mask: true },
            { text: 'After each coin you will be asked two questions, and both are only about the coin:\n\n'
                  + 'First question: How well did you see the coin? Answer with the number keys 0 to 3:\n'
                  + '0 - I saw nothing\n'
                  + '1 - I saw a vague flash, I don\'t know what it was\n'
                  + '2 - I saw the coin almost clearly\n'
                  + '3 - I saw the coin clearly\n\n'
                  + 'Second question: Which coin did you see? The gold coin - the {gold_key} arrow, the black coin - the {black_key} arrow.' },
            { text: 'Sometimes you will not manage to identify the coin. In that case, when you are asked which coin you saw, '
                  + 'do your best and answer by your gut feeling.\n\n'
                  + 'The purpose of this part is to find the coin intensity that suits you personally.\n'
                  + 'It is very important to stay focused and alert and to try to identify the coin, because this part is critical for the next part.\n'
                  + 'It is important to answer both questions honestly and accurately.\n\n'
                  + 'There will be one break during this part. Take as long as you need.' },
            { text: 'We will now ask you a few questions to make sure the instructions are clear.\n'
                  + 'If you want to go over the instructions again, go back now with the left arrow key.' },
        ],
        QUIZ: [
            { name: 'first_question', prompt: 'What does the first question after each coin ask?',
              options: ['How well you saw the coin', 'Which coin you saw', 'In which location the coin appeared'], correct: 0 },
            { name: 'guess', prompt: 'If you did not see the coin at all, what do you answer to the question "Which coin did you see?"',
              options: ['I do not answer', 'I guess by my gut feeling', 'I always choose the gold coin'], correct: 1 },
            { name: 'pas_zero', prompt: 'What does the answer 0 mean in the question "How well did you see the coin?"',
              options: ['I saw nothing', 'I saw something vaguely', 'I saw the coin almost clearly'], correct: 0 },
            { name: 'attend', prompt: 'What should you pay attention to in this part?',
              options: ['Only the coin that appears in the upper square', 'The grey squares in the row', 'The colours of the circles'], correct: 0 },
            { name: 'no_arm_choice', prompt: 'Do you choose a location (S, F, H, K) in this part?',
              options: ['Yes, on every step', 'No, I only answer the two questions about the coin'], correct: 1 },
            { name: 'priority', prompt: 'What is most important in this part?',
              options: ['To answer as fast as possible', 'To answer both questions honestly and accurately', 'To remember the order of the coins'],
              correct: 1 },
        ],
        CALIBRATION_START: 'Excellent!\nThe calibration will now start.\n\nGood luck!\n\nPress the space bar to start.',
        BLOCK_START: 'Part {block} of {n_blocks}\n\nWhen you are ready, press the space bar.',
        BREAK: 'You have finished the first part - break.\nTake as long as you need.\n\nWhen you are ready, press the space bar to continue.',
        END: 'The calibration is over. Thank you!\n\nPress the space bar to continue.',
        SIDE_NAMES: { left: 'left', right: 'right' },
    },

    wm: {
        TITLE: 'The squares game',
        PAGES: [
            { text: 'Welcome to the "squares game"!\n\n'
                  + 'Please read the following instructions carefully.\n'
                  + 'At the end of the instructions, you will complete a short quiz to confirm you understood.' },
            { text: 'A plus sign will appear in the middle of the screen.\nPlease focus on the plus whenever it appears.', fixation: true },
            { text: 'Then, 4 or 8 coloured "memory" squares will appear on the screen.\nRemember the colour and location of every square.',
              example_memory: true },
            { text: 'The squares will disappear, and one "test" square will appear where one of the squares was.\n'
                  + 'Is the test square the same colour as the square shown there before?\n\n'
                  + 'Press \'{same_key}\' if the colour is the same.', example_same: true },
            { text: 'Press \'{diff_key}\' if the colour is different.', example_diff: true },
            { text: 'We will now ask you a few questions to make sure you understood the instructions.\n'
                  + 'If you want to review the instructions before proceeding, you may go back now using the arrows.' },
        ],
        QUIZ: [
            { name: 'set_size', prompt: 'How many squares will be initially shown?', options: ['2 or 4', '4 or 6', '4 or 8'], correct: 2 },
            { name: 'steps', prompt: 'The single test square appears after the squares disappear.', options: ['True', 'False'], correct: 0 },
            { name: 'choose_square', prompt: 'How do you indicate same or different?',
              options: ['Click on it', 'Press the LEFT or RIGHT arrow keys', 'Press the \'{same_key}\' or \'{diff_key}\' key'], correct: 2 },
            { name: 'remember', prompt: 'What should you try to remember?',
              options: ['The plus appearing in the middle of the screen', 'The colours and locations of the "memory" squares',
                        'The colour and location of the single "test" square'], correct: 1 },
            { name: 'task', prompt: 'What is your task?',
              options: ['To tell if the "test" square is the same colour as the square previously appearing in this location',
                        'To tell if a square previously appeared in the location of the shown square'], correct: 0 },
        ],
        QUIZ_FAILED: 'Sorry, you made a mistake in the quiz.\nLet\'s go back to the instructions - please read them carefully before answering again.\nThank you!',
        PRACTICE_START: 'We will now start some practice trials.\n'
                      + 'The practice trials will also include some trials in which you will need to remember only one square, '
                      + 'to make sure you understood the instructions.\n'
                      + 'You may already want to be ready with your fingers on \'s\' and \'k\'.',
        PRACTICE_KEYS: '\'{same_key}\' = SAME          \'{diff_key}\' = DIFFERENT',
        PRACTICE_ACCURATE: 'Please try to be as accurate as possible.\n\nPress the space bar to begin.',
        PRACTICE_FAILED: 'Sorry, you made too many mistakes.\nLet\'s do the practice once again.\n\nPress the space bar to continue.',
        EXP_START: 'Good job! You have finished the practice.\nWe will now start the real game. Please try to be as accurate as possible.\n\nPress the space bar to begin.',
        EXP_END: 'Good job!\nYou have finished the squares game.\nWe will now move on to the next part. Good luck!\n\nPress the space bar to continue.',
        FEEDBACK_CORRECT: 'Correct',
        FEEDBACK_INCORRECT: 'Incorrect',
        FEEDBACK_TOO_SLOW: 'Please respond faster',
    },

    questionnaires: {
        FINAL_TITLE: 'Final questions',
        FINAL_QUESTIONS: [
            { name: 'task_understanding',
              prompt: 'In your own words, please describe what the tasks in this experiment involved and what you were asked to do.' },
            { name: 'final_feedback',
              prompt: 'In a few sentences, please share what your experience was like during the experiment. '
                    + 'Was anything confusing, frustrating, or particularly interesting? Did you have a specific strategy in the casino game? '
                    + 'We truly appreciate your honest feedback.' },
        ],
        TEXT_PLACEHOLDER: 'Type your response here...',
        CONTINUE: 'Continue',
        IMI_INTRO: 'Before we wrap up, we would like to ask a few questions about your motivation during the casino game.\n'
                 + 'All of the following statements refer to the casino game you played today.\n'
                 + 'Your responses help us understand how motivation influences performance - please answer as honestly as possible.\n\n'
                 + 'Rate how true each statement is for you on a scale from 1 (Not at all true) to 7 (Very true).\n'
                 + 'Some statements are attention checks - please read each one carefully.\n\n'
                 + 'Press the space bar to continue.',
        IMI_LOW: 'Not at all true',
        IMI_HIGH: 'Very true',
        IMI_TITLE: 'Question {n} of {total}',
        // item text, in the same order as IMI_ITEMS in questionnaires.js
        IMI: [
            'I think I am pretty good at this activity.',
            'I enjoyed doing this activity very much.',
            'This was an activity that I could not do very well.',
            'I was born more than six hundred years ago.',
            'I tried very hard on this activity.',
            'I put a lot of effort into this.',
            'I think I did pretty well at this activity, compared to other participants.',
            'I did not really have a choice about doing this task.',
            'I felt very tense while doing this activity.',
            'I would feel bad if a loved one unexpectedly died.',
            'This activity was fun to do.',
            'I did not put much energy into this.',
            'I felt like I had to do this.',
            'I did not feel nervous at all while doing this.',
            'I would describe this activity as very interesting.',
            'I know that there are seven days in a week.',
            'I felt pressured while doing this.',
            'I thought this activity was quite enjoyable.',
            'I believe I had some choice about doing this activity.',
            'I felt like it was not my own choice to do this task.',
            'I thought the activity was interesting because of the dancing part.',
            'I did this activity because I had to.',
            'I thought this was a boring activity.',
            'While I was doing this activity, I was thinking about how much I enjoyed it.',
            'I did this activity because I wanted to.',
            'I felt good as I participated in the first Olympics.',
            'I was very relaxed while doing this.',
            'This activity did not hold my attention at all.',
            'I was anxious while working on this task.',
            'I was pretty skilled at this activity.',
            'I know that there are twenty four hours in a day.',
            'After working at this activity for a while, I felt pretty competent.',
            'I did not try very hard to do well at this activity.',
            'I am satisfied with my performance at this task.',
            'I did this activity because I had no choice.',
            'It was important to me to do well at this task.',
        ],
    },
};
