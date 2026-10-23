# -*- coding: utf-8 -*-
"""End-of-day questionnaires (Hebrew), ported from ioc-wm (js/motivation.js and the final
open questions in index.html). Hebrew translations by Claude, 23 Oct 2026 - to be reviewed (status report).

IMI items: (English original, Hebrew, category, reverse-scored, attention check, expected answer 1-7).
Scale: 1 = Not at all true ... 7 = Very true. In the original jsPsych code the attention checks
expected the first or last option (index 0 / 6); here that is 1 / 7.
"""

IMI_INTRO = ('לפני שנסיים, נרצה לשאול כמה שאלות על המוטיבציה שלכם במהלך משחק הקזינו.\n'
             'כל המשפטים הבאים מתייחסים למשחק הקזינו ששיחקתם היום.\n'
             'התשובות שלכם יעזרו לנו להבין איך מוטיבציה משפיעה על הביצוע - אנא ענו בכנות רבה ככל האפשר.\n\n'
             'דרגו עד כמה כל משפט נכון לגביכם, בסולם מ-1 (בכלל לא נכון) עד 7 (נכון מאוד).\n'
             'חלק מהמשפטים הם בדיקות קשב - אנא קראו כל משפט בעיון.')
IMI_LOW = 'בכלל לא נכון'
IMI_HIGH = 'נכון מאוד'
IMI_TITLE = 'משחק הקזינו - שאלה {n} מתוך {total}'

IMI_ITEMS = [
    ("I think I am pretty good at this activity.", "אני חושב/ת שאני די טוב/ה בפעילות הזו.", "Perceived Competence", False, False, None),
    ("I enjoyed doing this activity very much.", "נהניתי מאוד מהפעילות הזו.", "Interest/Enjoyment", False, False, None),
    ("This was an activity that I could not do very well.", "זו הייתה פעילות שלא הצלחתי לבצע טוב במיוחד.", "Perceived Competence", True, False, None),
    ("I was born more than six hundred years ago.", "נולדתי לפני יותר משש מאות שנה.", "Attention", False, True, 1),
    ("I tried very hard on this activity.", "התאמצתי מאוד בפעילות הזו.", "Effort/Importance", False, False, None),
    ("I put a lot of effort into this.", "השקעתי בזה מאמץ רב.", "Effort/Importance", False, False, None),
    ("I think I did pretty well at this activity, compared to other participants.", "אני חושב/ת שהצלחתי די טוב בפעילות הזו, בהשוואה למשתתפים אחרים.", "Perceived Competence", False, False, None),
    ("I did not really have a choice about doing this task.", "לא באמת הייתה לי ברירה אם לבצע את המשימה הזו.", "Perceived Choice", True, False, None),
    ("I felt very tense while doing this activity.", "הרגשתי מתוח/ה מאוד בזמן הפעילות הזו.", "Pressure/Tension", True, False, None),
    ("I would feel bad if a loved one unexpectedly died.", "הייתי מרגיש/ה רע אם אדם יקר לי היה מת באופן פתאומי.", "Attention", True, True, 7),
    ("This activity was fun to do.", "היה כיף לעשות את הפעילות הזו.", "Interest/Enjoyment", False, False, None),
    ("I did not put much energy into this.", "לא השקעתי בזה הרבה אנרגיה.", "Effort/Importance", True, False, None),
    ("I felt like I had to do this.", "הרגשתי שאני חייב/ת לעשות את זה.", "Perceived Choice", True, False, None),
    ("I did not feel nervous at all while doing this.", "לא הרגשתי לחוץ/ה בכלל בזמן שעשיתי את זה.", "Pressure/Tension", False, False, None),
    ("I would describe this activity as very interesting.", "הייתי מתאר/ת את הפעילות הזו כמעניינת מאוד.", "Interest/Enjoyment", False, False, None),
    ("I know that there are seven days in a week.", "אני יודע/ת שיש שבעה ימים בשבוע.", "Attention", True, True, 7),
    ("I felt pressured while doing this.", "הרגשתי תחת לחץ בזמן שעשיתי את זה.", "Pressure/Tension", True, False, None),
    ("I thought this activity was quite enjoyable.", "חשבתי שהפעילות הזו מהנה למדי.", "Interest/Enjoyment", False, False, None),
    ("I believe I had some choice about doing this activity.", "אני מאמין/ה שהייתה לי במידה מסוימת בחירה אם לעשות את הפעילות הזו.", "Perceived Choice", False, False, None),
    ("I felt like it was not my own choice to do this task.", "הרגשתי שזו לא הייתה הבחירה שלי לבצע את המשימה הזו.", "Perceived Choice", True, False, None),
    ("I thought the activity was interesting because of the dancing part.", "חשבתי שהפעילות מעניינת בגלל החלק של הריקודים.", "Attention", False, True, 1),
    ("I did this activity because I had to.", "עשיתי את הפעילות הזו כי הייתי חייב/ת.", "Perceived Choice", True, False, None),
    ("I thought this was a boring activity.", "חשבתי שזו פעילות משעממת.", "Interest/Enjoyment", True, False, None),
    ("While I was doing this activity, I was thinking about how much I enjoyed it.", "בזמן שעשיתי את הפעילות, חשבתי על כמה אני נהנה/ית ממנה.", "Interest/Enjoyment", False, False, None),
    ("I did this activity because I wanted to.", "עשיתי את הפעילות הזו כי רציתי.", "Perceived Choice", False, False, None),
    ("I felt good as I participated in the first Olympics.", "הרגשתי טוב כשהשתתפתי באולימפיאדה הראשונה.", "Attention", False, True, 1),
    ("I was very relaxed while doing this.", "הייתי רגוע/ה מאוד בזמן שעשיתי את זה.", "Pressure/Tension", False, False, None),
    ("This activity did not hold my attention at all.", "הפעילות הזו לא החזיקה את הקשב שלי בכלל.", "Interest/Enjoyment", True, False, None),
    ("I was anxious while working on this task.", "הייתי חרד/ה בזמן שעבדתי על המשימה הזו.", "Pressure/Tension", True, False, None),
    ("I was pretty skilled at this activity.", "הייתי די מיומן/ת בפעילות הזו.", "Perceived Competence", False, False, None),
    ("I know that there are twenty four hours in a day.", "אני יודע/ת שיש עשרים וארבע שעות ביממה.", "Attention", True, True, 7),
    ("After working at this activity for a while, I felt pretty competent.", "אחרי שעבדתי על הפעילות הזו זמן מה, הרגשתי די מסוגל/ת.", "Perceived Competence", False, False, None),
    ("I did not try very hard to do well at this activity.", "לא התאמצתי במיוחד להצליח בפעילות הזו.", "Effort/Importance", True, False, None),
    ("I am satisfied with my performance at this task.", "אני מרוצה מהביצועים שלי במשימה הזו.", "Perceived Competence", False, False, None),
    ("I did this activity because I had no choice.", "עשיתי את הפעילות הזו כי לא הייתה לי ברירה.", "Perceived Choice", True, False, None),
    ("It was important to me to do well at this task.", "היה לי חשוב להצליח במשימה הזו.", "Effort/Importance", False, False, None),
]

FINAL_TITLE = 'שאלה לסיום'
FINAL_QUESTIONS = [
    ('task_understanding',
     'In your own words, please describe what the tasks in this experiment involved and what you were asked to do.',
     'במילים שלכם, תארו בבקשה מה כללו המשימות בניסוי ומה התבקשתם לעשות.'),
    ('final_feedback',
     'In a few sentences, please share what your experience was like during the experiment. '
     'Was anything confusing, frustrating, or particularly interesting? We truly appreciate your honest feedback.',
     'בכמה משפטים, שתפו בבקשה איך הייתה החוויה שלכם בניסוי. האם משהו היה מבלבל, מתסכל או מעניין במיוחד? '
     'נשמח מאוד למשוב כנה.'),
]
TEXT_FOOTER = 'הקלידו את תשובתכם. לסיום לחצו Enter'
TEXT_TOO_SHORT = 'אנא כתבו תשובה לפני שתמשיכו.'
