#!/usr/bin/env python

"""Pull a message of each type from an input file list"""

import os
import sys
import json

if (len(sys.argv) < 3):
    print "Usage: %s <out_dir/> <actions.json> [actions2.json, ...]" % sys.argv[0]
    sys.exit(1)

OUT_DIR = sys.argv[1]
ACTION_FILES = sys.argv[2:]

if not os.path.isdir(OUT_DIR):
    os.mkdir(OUT_DIR)


def save_obj(name, o):
    with open('%s/%s.json' % (OUT_DIR, name), 'w') as f:
        json.dump(o, f, indent=2, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(',', ': '))

def keys_to_list(o):
    ordered_keys = []
    for k in sorted(o):
        # Ignore shortLink presence (it varies) as we don't use it
        if k == 'shortLink':
            continue
        # Don't recurse for labelNames
        if (type(o[k]) == dict) and (k != 'labelNames'):
            ordered_keys.append( keys_to_list(o[k]) )
        else:
            ordered_keys.append( k )
    return ordered_keys


saved_actions = {}
update_actions = {}

action_list = []


for file_name in ACTION_FILES: 
    print 'processing', file_name

    with open(file_name) as f:
        json_dict = json.loads(f.read())

    if 'boards' in json_dict:
        for b in json_dict['boards']:
            action_list += b['actions']
    elif 'actions' in json_dict:
        action_list += json_dict['actions']

    for a in action_list:
        t = a['type']
        if t.find('update') != -1:
            cur_list = update_actions.get(t, [])
            a_keys = keys_to_list(a)
            do_save = True
            for l in cur_list:
                if a_keys == l:
                    do_save = False
                    break
            if do_save:
                cur_list.append(a_keys)
                update_actions[t] = cur_list
                name = '%s_%d' % (t, len(cur_list))
                save_obj(name, a)
        elif t not in saved_actions:
            saved_actions[t] = True
            save_obj(t, a)


