# -*- coding: utf-8 -*-
"""Master builder for cytset 30-day curriculum (assets/lessons_data.js)"""

import sys
import os
import json

# Add curriculum path
curriculum_dir = os.path.join(os.path.dirname(__file__), "curriculum")
sys.path.insert(0, curriculum_dir)

from week1 import WEEK_1_LESSONS
from week2 import WEEK_2_LESSONS
from week3 import WEEK_3_LESSONS
from week4 import WEEK_4_LESSONS
from week5 import WEEK_5_LESSONS

all_lessons = WEEK_1_LESSONS + WEEK_2_LESSONS + WEEK_3_LESSONS + WEEK_4_LESSONS + WEEK_5_LESSONS

print("==================================================")
print(f"Total days loaded: {len(all_lessons)}")

# Validation
assert len(all_lessons) == 30, f"Expected 30 days, got {len(all_lessons)}"

question_ids = set()
total_questions = 0

for idx, lesson in enumerate(all_lessons, 1):
    day = lesson["day"]
    assert day == idx, f"Day mismatch at index {idx}: got {day}"
    questions = lesson["questions"]
    assert len(questions) == 9, f"Day {day} must have exactly 9 questions, got {len(questions)}"
    
    for q_idx, q in enumerate(questions, 1):
        qid = q.get("id")
        assert qid, f"Missing id in day {day} question {q_idx}"
        assert qid not in question_ids, f"Duplicate question id {qid}"
        question_ids.add(qid)
        assert len(q["options"]) == 4, f"Question {qid} must have 4 options"
        assert 0 <= q["correct"] < 4, f"Invalid correct index in {qid}"
        assert len(q["q"]) > 5, f"Question text too short in {qid}"
        assert len(q["explain"]) > 10, f"Explanation too short in {qid}"
        total_questions += 1

print(f"Validation successful! Total validated questions: {total_questions} (9 per day)")

out_path = os.path.join(os.path.dirname(__file__), "assets", "lessons_data.js")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("// CYTSET 30-DAY COMPREHENSIVE INFOSEC CURRICULUM (270 QUESTIONS)\n")
    f.write("// Generated automatically by build_lessons.py\n")
    f.write("const LESSONS_DATA = " + json.dumps(all_lessons, ensure_ascii=False, indent=2) + ";\n")

print(f"Successfully saved to: {out_path} ({os.path.getsize(out_path):,} bytes)")
print("==================================================")
