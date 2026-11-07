# -*- coding: utf-8 -*-
"""Writes online/js/texts_he.js from the lab's Hebrew texts (texts/*.py), so both versions stay in sync.

Run from the repository root after changing any file in texts/:
    python online/tools/export_hebrew_texts.py

Strings that exist only in the online version (Prolific, fullscreen, mouse quizzes, ...) are in
ONLINE_ONLY below (Hebrew by Claude - to be reviewed). The key structure matches js/texts_en.js.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
from texts import awareness as A, bandit as B, calibration as C, common as CO, wm as W, questionnaires as Q  # noqa: E402

ONLINE_ONLY = {
    'common': {
        'NEXT': 'הבא', 'PREV': 'הקודם',
        'NAV_HINT': 'מעבר בין העמודים בעזרת החצים (&larr; הבא, &rarr; הקודם) או הכפתורים למטה.',
        'QUIZ_SUBMIT': 'שליחת התשובות',
        'QUIZ_PREAMBLE': 'אנא ענו על כל השאלות כדי לוודא שההוראות ברורות.',
        'BACK_TO_INSTRUCTIONS': 'חזרה להוראות',
        'MOBILE_TITLE': 'הניסוי דורש מחשב שולחני או נייד.',
        'MOBILE_TEXT': 'נראה שאתם משתמשים בטלפון או בטאבלט.\nלא ניתן להשתתף במכשיר זה.\nאנא חזרו כשתהיה לכם גישה למחשב.',
        'MOBILE_BUTTON': 'יציאה',
        'CAPTCHA': 'אנא השלימו את בדיקת ה-CAPTCHA כדי להמשיך.', 'CAPTCHA_SUBMIT': 'שליחה',
        'CAPTCHA_ALERT': 'אנא השלימו את בדיקת ה-CAPTCHA.',
        'FULLSCREEN': 'הניסוי פועל במסך מלא.\n'
                      'אנא ודאו שהדפדפן בזום 100%, סגרו תוכנות ולשוניות אחרות והשתיקו התראות.\n'
                      'שבו בנוחות במרחק יד מהמסך, והסתכלו על המסך לאורך כל הניסוי.',
        'FULLSCREEN_BUTTON': 'לחצו כאן כדי לעבור למסך מלא',
        'PAUSE_ALERT': 'הניסוי הושהה. במידת הצורך חזרו למסך מלא בעזרת F11. אנא הישארו מרוכזים בניסוי עד סופו.',
        'WELCOME_DAY1': 'ברוכים הבאים ותודה על השתתפותכם!\n\n'
                        'הניסוי כולל שני חלקים בשני ימים נפרדים: היום ומחר. '
                        'לאחר סיום החלק של היום תקבלו הזמנה לחלק השני. '
                        'אנא השתתפו רק אם תוכלו להשלים את שני החלקים.\n\n'
                        'היום תשחקו בשני משחקים: "משחק הריבועים" ו"משחק הקזינו", ולאחר מכן תענו על כמה שאלות.\n'
                        'אנא הישארו קשובים ובמסך מלא לאורך כל הניסוי.',
        'WELCOME_DAY2': 'ברוכים השבים ותודה על השתתפותכם בחלק השני של הניסוי!\n\n'
                        'היום תהיה מטלת מטבעות קצרה, אחריה משחק הקזינו ששיחקתם אתמול, ולבסוף כמה שאלות.\n'
                        'אנא הישארו קשובים ובמסך מלא לאורך כל הניסוי.',
        'WELCOME_CONTINUE': 'לחצו על מקש הרווח כדי להמשיך.',
        'DAY_END': 'סיימתם את החלק של היום.\nתודה רבה!',
        'UPLOADING': 'אנא המתינו רגע בזמן שהנתונים נשמרים...',
        'REDIRECT': 'אנא המתינו, בעוד רגע תועברו חזרה.\n\nאם מופיעה אזהרה שהנתונים עלולים לא להישמר, אפשר ללחוץ "עזיבה" - הנתונים כבר נשמרו.',
        'REDIRECT_LINK': 'אם לא הועברתם אוטומטית, לחצו כאן:',
        'THANK_YOU_END': 'תודה רבה! אפשר לסגור את החלון.',
        'DAY_STOPPED': 'החלק הזה של הניסוי הסתיים.\nתודה על השתתפותכם.',
        'DAY_STOPPED_BUTTON': 'המשך',
        'QUIZ_OUT': 'לצערנו טעיתם בשאלות {n} פעמים.\nלכן עלינו לסיים כאן את הניסוי.\n\nתודה על זמנכם. כעת תועברו חזרה.',
        'CALIB_ERROR': 'אירעה שגיאה, ועלינו לסיים כאן את השתתפותכם בניסוי.\nתקבלו תשלום על השתתפותכם בכל מקרה.\n\nתודה רבה!',
        'REFRESH_MEASURING': 'מכינים את הניסוי, אנא המתינו...',
    },
    'wm': {
        'PRACTICE_START': 'כעת נתחיל כמה צעדי אימון.\n'
                          'האימון יכלול גם צעדים שבהם תצטרכו לזכור ריבוע אחד בלבד, כדי לוודא שהבנתם את ההוראות.\n'
                          'כדאי כבר להניח את האצבעות על המקשים s ו-k.',
        'PRACTICE_KEYS': '{same_key} = אותו צבע          {diff_key} = צבע שונה',
        'PRACTICE_ACCURATE': 'אנא נסו להיות מדויקים ככל האפשר.\n\nלחצו על מקש הרווח כדי להתחיל.',
    },
    'questionnaires': {
        'TEXT_PLACEHOLDER': 'הקלידו כאן את תשובתכם...',
        'CONTINUE': 'המשך',
    },
}

SPACE = '\n\n' + CO.PRESS_SPACE   # lab messages are shown with a "press space" footer; online it is part of the text


def pages(specs):
    return [dict(s) for s in specs]


n_rules = len(B._COMMON_RULES)
he = {
    'dir': 'rtl',
    'common': {
        'QUIZ_FAILED': CO.QUIZ_FAILED, 'PRESS_SPACE': CO.PRESS_SPACE, 'BREAK': CO.BREAK,
        'DAY_STOPPED': CO.DAY_STOPPED,
    },
    'awareness': {'PAS_QUESTION': A.PAS_QUESTION, 'PAS_OPTIONS': A.PAS_OPTIONS, 'PAS_FOOTER': A.PAS_FOOTER,
                  'CHOICE_QUESTION': A.CHOICE_QUESTION, 'CHOICE_FOOTER': A.CHOICE_FOOTER},
    'bandit': {
        'TITLE': B.TITLE, 'TITLE_DAY2': B.TITLE_DAY2,
        'PAGES_DAY1_INTRO': pages(B.PAGES_DAY1[:1]), 'PAGES_DAY2_INTRO': pages(B.PAGES_DAY2[:1]),
        'PAGES_RULES': pages(B._COMMON_RULES), 'PAGE_MASK_DAY2': dict(B.PAGES_DAY2[1 + n_rules]),
        'PAGES_TIPS': pages(B._COMMON_TIPS), 'PROBE_SENTENCE': B.PROBE_SENTENCE, 'QUIZ': B.QUIZ,
        'PRACTICE_START': B.PRACTICE_START + SPACE, 'PRACTICE_END': B.PRACTICE_END + SPACE,
        'TOO_LATE': B.TOO_LATE, 'UNAVAILABLE': B.UNAVAILABLE, 'BREAK': B.BREAK,
        'END_WITH_TOTAL': B.END_WITH_TOTAL + SPACE, 'END_NO_TOTAL': B.END_NO_TOTAL + SPACE,
    },
    'calibration': {
        'TITLE': C.TITLE, 'PAGES': pages(C.PAGES), 'QUIZ': C.QUIZ,
        'CALIBRATION_START': C.CALIBRATION_START + SPACE, 'BLOCK_START': C.BLOCK_START, 'BREAK': C.BREAK,
        'END': C.END + SPACE, 'SIDE_NAMES': C.SIDE_NAMES,
    },
    'wm': {
        'TITLE': W.TITLE, 'PAGES': pages(W.PAGES), 'QUIZ': W.QUIZ, 'QUIZ_FAILED': W.QUIZ_FAILED,
        'PRACTICE_FAILED': W.PRACTICE_FAILED + SPACE, 'EXP_START': W.EXP_START + SPACE, 'EXP_END': W.EXP_END + SPACE,
        'FEEDBACK_CORRECT': W.FEEDBACK_CORRECT, 'FEEDBACK_INCORRECT': W.FEEDBACK_INCORRECT,
        'FEEDBACK_TOO_SLOW': W.FEEDBACK_TOO_SLOW,
    },
    'questionnaires': {
        'FINAL_TITLE': Q.FINAL_TITLE,
        'FINAL_QUESTIONS': [{'name': n, 'prompt': h} for n, _, h in Q.FINAL_QUESTIONS],
        'IMI_INTRO': Q.IMI_INTRO + SPACE, 'IMI_LOW': Q.IMI_LOW, 'IMI_HIGH': Q.IMI_HIGH,
        'IMI_TITLE': 'שאלה {n} מתוך {total}',
        'IMI': [item[1] for item in Q.IMI_ITEMS],
    },
}
for section, values in ONLINE_ONLY.items():
    he[section].update(values)

# ONLINE: money bonus (the lab version has no money) - Hebrew by Claude, to be reviewed
he['bandit']['PAGES_RULES'][0]['text'] = ('במהלך המשחק יש לבצע בחירות כדי לנסות ולזכות במטבעות זהב.\n'
                                          'כל מטבע זהב מוסיף {win} לבונוס כספי אמיתי. מטבע זהב נראה כך:')
he['bandit']['PAGES_RULES'][1]['text'] = 'אם לא זכיתם, יוצג המטבע הכסוף הבא, ו-{loss} יורדים מהבונוס שלכם (הבונוס לעולם לא יורד מתחת ל-{zero}):'
he['bandit']['PAGES_TIPS'][2]['text'] = ('הבונוס שלכם לא מוצג במהלך המשחק. הוא נספר, מוצג בסוף המשחק ומשולם לכם בנוסף לתשלום הבסיסי. '
                                         'מטרתכם היא לבחור במיקומים הנכונים על מנת לצבור כמה שיותר מטבעות זהב!\n\n'
                                         'במשחק {n_trials} צעדי בחירה, עם {n_breaks} הפסקות. זכרו: המטרה היא לזכות בכמה שיותר מטבעות.')
quiz = he['bandit']['QUIZ']
quiz.insert(len(quiz) - 1, {'name': 'bonus', 'prompt': 'מה קורה כשמוצג המטבע הכסוף?',
                            'options': ['שום דבר', '{loss} יורדים מהבונוס שלי (הוא לא יורד מתחת ל-{zero})', 'אני מאבד/ת את כל הבונוס'],
                            'correct': 1})
he['bandit']['END_WITH_TOTAL'] = 'המשחק הסתיים!\n\nהבונוס שלכם מהמשחק: {bonus}.' + SPACE

out = os.path.join(ROOT, 'online', 'js', 'texts_he.js')
with open(out, 'w', encoding='utf-8') as f:
    f.write('// ─── texts_he.js ── GENERATED by online/tools/export_hebrew_texts.py from texts/*.py - do not edit by hand.\n')
    f.write('// Same keys as texts_en.js. Online-only strings: ONLINE_ONLY in the generator (Hebrew by Claude, to be reviewed).\n')
    f.write('var TEXTS_HE = ')
    f.write(json.dumps(he, ensure_ascii=False, indent=1))
    f.write(';\n')
print('wrote', out)
