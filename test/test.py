#!/usr/bin/env python

import difflib
import glob
import json
import os
import sys
import traceback

TEST_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(TEST_DIR, '..'))

from action import Action
from action_printer import ActionPrinter

passed = 0
failed = 0

os.chdir(os.path.join(TEST_DIR, 'actions'))
for action_file in glob.glob('*.json'):
    base_name = action_file[:-5]
    expected_file = base_name + '.expected'
    try:
        with open(action_file, 'r') as f:
            action_json = json.load(f)
        if os.path.exists(expected_file):
            with open(expected_file, 'r') as f:
                expected = f.read()
                if type(expected) != unicode:
                    expected = expected.decode('utf-8')
        else:
            expected = ''

        a = Action(action_json)
        a_p = ActionPrinter()
        actual = a_p.get_message(a)
        if actual is None:
            actual = ''

        saw_diff = False
        for d in difflib.unified_diff([expected], [actual], fromfile='expected', tofile='actual', lineterm=''):
            if not saw_diff:
                print base_name
                saw_diff = True
            print '  ', d.replace('\n', '\n   ')

        if saw_diff:
            failed += 1
            with open(base_name + '.actual', 'w') as f:
                f.write(actual.encode('utf-8'))
            print ''
        else:
            passed += 1
    except Exception as e:
        failed += 1
        print action_file
        print '  ', traceback.format_exc().replace('\n', '\n   ').strip()
        print ''

print passed, 'passed,', failed, 'failed'

if failed > 0:
    sys.exit(1)

