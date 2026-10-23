"""Participant-facing screens: text pages, instructions, quiz, Likert items, breaks.

All text comes from the texts/ package (Hebrew, right-to-left); this module
only lays it out. Everything is keyboard-driven.

Instruction page format (a dict):
    {'title': str (optional),
     'text': str,
     'images': [(path_relative_to_stimuli, (x, y), (w, h)), ...] (optional),
     'draw': callable that draws extra content, e.g. a live casino-scene example (optional)}

Quiz question format (a dict):
    {'name': short id for the data file,
     'prompt': str,
     'options': [str, ...],
     'correct': index of the correct option (0-based)}
"""
import os

from psychopy import visual, core
from psychopy.tools.monitorunittools import deg2pix

import config
from common.display import show
from common.keyboard import number_keys_for, number_key_value
from texts import common as T


class Screens:
    def __init__(self, win, keys):
        self.win = win
        self.keys = keys
        # PsychoPy's own wrapping reverses the line order of right-to-left paragraphs, so
        # text is wrapped here (_wrap) and the stimuli get a wrap width they never reach.
        style = dict(font=config.FONT, languageStyle=config.LANGUAGE_STYLE,
                     color=config.TEXT_COLOR, wrapWidth=config.TEXT_WRAP_WIDTH * 3)
        self.title = visual.TextStim(win, pos=(0, config.TITLE_Y), height=config.TITLE_HEIGHT,
                                     anchorVert='top', bold=True, **style)
        self.body = visual.TextStim(win, pos=(config.TEXT_WRAP_WIDTH / 2, config.BODY_TOP_Y),
                                    height=config.TEXT_HEIGHT, anchorVert='top', anchorHoriz='right',
                                    alignText='right', **style)
        self.center = visual.TextStim(win, pos=(0, 0), height=config.TEXT_HEIGHT,
                                      alignText='center', **style)
        self.footer = visual.TextStim(win, pos=config.FOOTER_POS, height=config.FOOTER_HEIGHT,
                                      **style)
        self.option_number = visual.TextStim(win, height=config.TEXT_HEIGHT, anchorHoriz='right', alignText='right',
                                             bold=True, **style)
        self.option_text = visual.TextStim(win, height=config.TEXT_HEIGHT, anchorHoriz='right',
                                           alignText='right', **style)
        self.scale_point = visual.TextStim(win, height=config.TEXT_HEIGHT * 1.3, bold=True, **style)
        self.scale_anchor = visual.TextStim(win, height=config.FOOTER_HEIGHT, **{**style, 'wrapWidth': 8})
        self._images = {}
        self._measure = visual.TextStim(win, font=config.FONT, languageStyle=config.LANGUAGE_STYLE,
                                        wrapWidth=1e4, autoLog=False)
        self._wrapped = {}

    # ── helpers ──────────────────────────────────────────────────────────────
    def set_text_color(self, color):
        """Change the colour of all text (e.g. dark text on the WM task's light background)."""
        for stim in (self.title, self.body, self.center, self.footer, self.option_number,
                     self.option_text, self.scale_point, self.scale_anchor):
            stim.color = color

    def wrap(self, text, height, width=None):
        """Break text into lines no wider than width (deg), keeping explicit line breaks."""
        width = config.TEXT_WRAP_WIDTH if width is None else width
        key = (text, height, width)
        if key not in self._wrapped:
            max_pix = deg2pix(width, self.win.monitor)
            self._measure.height = height
            lines = []
            for paragraph in text.split('\n'):
                line = ''
                for word in paragraph.split(' '):
                    candidate = f'{line} {word}' if line else word
                    self._measure.text = candidate
                    if line.strip() and self._measure.boundingBox[0] > max_pix:
                        lines.append(line)
                        line = word
                    else:
                        line = candidate
                lines.append(line)
            self._wrapped[key] = '\n'.join(lines)
        return self._wrapped[key]

    def _image(self, path, pos, size):
        key = (path, tuple(pos), tuple(size))
        if key not in self._images:   # created once, re-used on every later visit
            self._images[key] = visual.ImageStim(self.win, image=os.path.join(config.STIMULI_DIR, path),
                                                 pos=pos, size=size)
        return self._images[key]

    def _draw_page(self, page, footer=''):
        if page.get('title'):
            self.title.text = page['title']
            self.title.draw()
        self.body.text = self.wrap(page.get('text', ''), config.TEXT_HEIGHT)
        self.body.draw()
        for path, pos, size in page.get('images', []):
            self._image(path, pos, size).draw()
        if page.get('draw'):
            page['draw']()
        if footer:
            self.footer.text = footer
            self.footer.draw()

    # ── simple screens ───────────────────────────────────────────────────────
    def message(self, text, keys=None, footer=None, min_duration=0.0):
        """Centered text; waits for a key (default: continue key). Returns the key."""
        keys = keys or [config.CONTINUE_KEY]
        footer = T.PRESS_SPACE if footer is None else footer

        def draw(with_footer):
            self.center.text = self.wrap(text, config.TEXT_HEIGHT)
            self.center.draw()
            if with_footer and footer:
                self.footer.text = footer
                self.footer.draw()

        if min_duration > 0:                       # text visible, keys locked
            show(self.win, lambda: draw(False))
            self._locked_wait(min_duration)
        self.keys.clear()
        show(self.win, lambda: draw(True))
        key, _ = self.keys.wait(keys)
        return key

    def blank(self, duration):
        show(self.win, lambda: None, duration)

    def _locked_wait(self, duration):
        timer = core.Clock()
        while timer.getTime() < duration:
            self.keys.check_abort()
            core.wait(0.05)

    def break_screen(self, text=None, min_duration=0.0):
        return self.message(text or T.BREAK, min_duration=min_duration)

    # ── instructions ─────────────────────────────────────────────────────────
    def instructions(self, pages):
        """Show pages; next/previous with the arrow keys. Returns when the last page is passed."""
        i = 0
        while i < len(pages):
            first, last = i == 0, i == len(pages) - 1
            footer = T.NAV_FIRST if first else (T.NAV_LAST if last else T.NAV_MIDDLE)
            self.keys.clear()
            show(self.win, lambda: self._draw_page(pages[i], footer))
            allowed = [config.INSTR_NEXT_KEY] + ([] if first else [config.INSTR_PREV_KEY])
            key, _ = self.keys.wait(allowed)
            i += 1 if key == config.INSTR_NEXT_KEY else -1

    # ── quiz ─────────────────────────────────────────────────────────────────
    def quiz(self, questions, log=None, attempt=1):
        """Ask every question (one per screen), THEN check. Returns True if all correct.

        log: optional function(row_dict) - called once per question.
        """
        answers = []
        for q_num, q in enumerate(questions, start=1):
            chosen, rt = self.choice(q['prompt'], q['options'],
                                     title=T.QUIZ_TITLE.format(n=q_num, total=len(questions)))
            answers.append(chosen)
            if log:
                log({'phase': 'quiz', 'quiz_attempt': attempt, 'quiz_question': q['name'],
                     'quiz_response': chosen, 'quiz_correct_answer': q['correct'],
                     'quiz_is_correct': int(chosen == q['correct']), 'rt': rt})
        return all(a == q['correct'] for a, q in zip(answers, questions))

    def _draw_options(self, options, start=1):
        """Answer rows under the question: number at the right edge, text to its left."""
        right = config.TEXT_WRAP_WIDTH / 2
        for i, text in enumerate(options):
            y = config.QUIZ_OPTIONS_TOP_Y - i * config.QUIZ_OPTION_SPACING
            self.option_number.text = f'{start + i}'
            self.option_number.pos = (right, y)
            self.option_number.draw()
            self.option_text.text = self.wrap(text, config.TEXT_HEIGHT,
                                              config.TEXT_WRAP_WIDTH - config.QUIZ_NUMBER_COLUMN_WIDTH)
            self.option_text.pos = (right - config.QUIZ_NUMBER_COLUMN_WIDTH, y)
            self.option_text.draw()

    def choice(self, prompt, options, title='', start=1, footer=None):
        """A question with numbered options answered by number keys (start..start+n-1).

        Returns (chosen index 0-based, rt from the screen onset).
        """
        page = {'title': title, 'text': prompt,
                'draw': lambda: self._draw_options(options, start)}
        self.keys.clear()
        self.keys.reset_clock_on_flip(self.win)
        show(self.win, lambda: self._draw_page(page, T.QUIZ_FOOTER if footer is None else footer))
        key, rt = self.keys.wait(number_keys_for(len(options), start=start))
        return number_key_value(key) - start, rt

    def instructions_with_quiz(self, pages, questions, log=None, fail_text=None):
        """Instructions -> quiz; on any mistake show fail_text and start over. Returns n attempts."""
        attempt = 1
        while True:
            self.instructions(pages)
            if self.quiz(questions, log=log, attempt=attempt):
                return attempt
            self.message(fail_text or T.QUIZ_FAILED)
            attempt += 1

    # ── Likert item ──────────────────────────────────────────────────────────
    def likert(self, prompt, n_points=7, low_label='', high_label='', title=''):
        """One statement, answered with keys 1..n_points. Returns (value, rt)."""
        page = {'title': title, 'text': prompt,
                'draw': lambda: self._draw_scale(n_points, low_label, high_label)}
        self.keys.clear()
        self.keys.reset_clock_on_flip(self.win)
        show(self.win, lambda: self._draw_page(page, T.LIKERT_FOOTER.format(n=n_points)))
        key, rt = self.keys.wait(number_keys_for(n_points))
        return number_key_value(key), rt

    def _draw_scale(self, n_points, low_label, high_label):
        """Points 1..n in a row; 1 on the right when LIKERT_LOW_ON_RIGHT (Hebrew reading order)."""
        half = config.LIKERT_WIDTH / 2
        direction = -1 if config.LIKERT_LOW_ON_RIGHT else 1
        xs = [direction * (-half + i * config.LIKERT_WIDTH / (n_points - 1)) for i in range(n_points)]
        for value, x in enumerate(xs, start=1):
            self.scale_point.text = str(value)
            self.scale_point.pos = (x, config.LIKERT_Y)
            self.scale_point.draw()
        for label, x in ((low_label, xs[0]), (high_label, xs[-1])):
            if label:
                self.scale_anchor.text = label
                self.scale_anchor.pos = (x, config.LIKERT_Y - 1.6)
                self.scale_anchor.draw()

    # ── free text ────────────────────────────────────────────────────────────
    def text_entry(self, prompt, title='', footer='', too_short='', min_chars=1):
        """Typed answer (any keyboard layout, e.g. Hebrew). Enter submits, Backspace deletes.

        Characters are taken from the window's text events and shown with the same
        right-to-left TextStim used everywhere else (PsychoPy's editable TextBox2
        stores Hebrew in reversed order). Returns (text, rt from the screen onset).
        """
        typed = []
        warn = ''

        def on_text(text):
            if text not in ('\r', '\n'):
                typed.append(text)

        box = visual.Rect(self.win, width=config.TEXT_WRAP_WIDTH + 1, height=config.TEXT_ENTRY_HEIGHT,
                          pos=(0, config.TEXT_ENTRY_Y), lineColor=self.center.color, fillColor=None)
        self.keys.clear()
        self.keys.reset_clock_on_flip(self.win)
        self.win.winHandle.push_handlers(on_text=on_text)
        try:
            while True:
                answer = ''.join(typed)
                self.center.pos = (0, config.TEXT_ENTRY_Y)
                self.center.text = self.wrap(answer + '_', config.TEXT_HEIGHT)   # '_' = typing cursor
                page = {'title': title, 'text': prompt + (('\n\n' + warn) if warn else '')}
                self._draw_page(page, footer)
                box.draw()
                self.center.draw()
                self.win.flip()
                for key in self.keys.kb.getKeys(['backspace', 'return', 'num_enter', config.ABORT_KEY],
                                                waitRelease=False, clear=True):
                    if key.name == config.ABORT_KEY:
                        from common.keyboard import AbortExperiment
                        raise AbortExperiment()
                    if key.name == 'backspace' and typed:
                        typed.pop()
                    elif key.name in ('return', 'num_enter'):
                        if len(answer.strip()) >= min_chars:
                            return answer.strip(), key.rt
                        warn = too_short
        finally:
            self.win.winHandle.pop_handlers()
            self.center.pos = (0, 0)

