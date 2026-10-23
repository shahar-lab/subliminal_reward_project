"""End-of-day questionnaires (both days), ported from ioc-wm in the same order:
the two open questions (typed), then the 36-item IMI (one statement per screen, keys 1-7)
with 6 attention checks. One row per question; a summary row with the number of failed
attention checks and IMI subscale means (reverse-scored items as 8 - response).
"""
import config
from common.io import TaskData
from texts import questionnaires as T

TASK = 'questionnaires'


def run_day1(ctx):
    return run(ctx)


def run_day2(ctx):
    return run(ctx)


def score_imi(rows):
    """Failed attention checks and per-category means (reverse-scored items flipped)."""
    failed = sum(r['attention'] and r['response'] != r['expected_answer'] for r in rows)
    by_cat = {}
    for r in rows:
        if r['attention']:
            continue
        value = 8 - r['response'] if r['reverse_scored'] else r['response']
        by_cat.setdefault(r['category'], []).append(value)
    means = {f'imi_{c.lower().replace("/", "_").replace(" ", "_")}': sum(v) / len(v) for c, v in by_cat.items()}
    return failed, means


def run(ctx):
    with TaskData(ctx.participant, TASK, ctx.runtime) as td:
        if config.QUESTIONNAIRE_FINAL_QUESTIONS:
            for name, english, hebrew in T.FINAL_QUESTIONS:
                answer, rt = ctx.screens.text_entry(hebrew, title=T.FINAL_TITLE, footer=T.TEXT_FOOTER,
                                                    too_short=T.TEXT_TOO_SHORT, min_chars=config.TEXT_MIN_CHARS)
                td.add_row({'phase': 'final_questions', 'question': name, 'prompt_en': english,
                            'answer': answer, 'rt': rt})

        if config.QUESTIONNAIRE_IMI:
            ctx.screens.message(T.IMI_INTRO)
            rows = []
            for i, (english, hebrew, category, reverse, attention, expected) in enumerate(T.IMI_ITEMS, start=1):
                value, rt = ctx.screens.likert(hebrew, n_points=7, low_label=T.IMI_LOW, high_label=T.IMI_HIGH,
                                               title=T.IMI_TITLE.format(n=i, total=len(T.IMI_ITEMS)))
                row = {'phase': 'imi', 'question_index': i, 'prompt_en': english, 'category': category,
                       'reverse_scored': int(reverse), 'attention': int(attention), 'expected_answer': expected,
                       'response': value, 'rt': rt,
                       'attention_failed': int(value != expected) if attention else None}
                rows.append({**row, 'reverse_scored': reverse, 'attention': attention})
                td.add_row(row)
            failed, means = score_imi(rows)
            td.add_row({'phase': 'imi', 'event': 'imi_summary', 'failed_attention_checks': failed, **means})
            print(f'IMI: {failed} failed attention checks; ' +
                  ', '.join(f'{k}={v:.2f}' for k, v in means.items()))
