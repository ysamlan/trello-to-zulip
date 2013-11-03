#!/usr/bin/env python

'''Remove all IDs, names, hashes, etc from action files'''

import sys
import json
import datetime

NOW_DATETIME = datetime.datetime.utcnow().isoformat()[:23] + 'Z'

REPLACEMENTS = {
    'data': {
        'attachment': {
            'id': 'attidattidattidattidatti',
            'name': 'att_file_name.ext',
            'previewUrl': 'https://example.com/preview_url',
            'url': 'https://example.com/url'
        },
        'board': {
            'id': 'b1idb1idb1idb1idb1idb1id',
            'name': 'Board One',
            'labelNames': {
                'red': 'Board One label name'
            },
            'shortLink': 'b1slb1sl'
        },
        'boardSource': {
            'id': 'b2idb2idb2idb2idb2idb2id',
            'name': 'Board Two'
        },
        "boardTarget": {
            "id": "btidbtidbtidbtidbtidbtid",
            "name": "Board Target Name"
        },
        'card': {
            'desc': 'Card Name description has multiple words of text. And stuff.',
            'due': NOW_DATETIME,
            'id': 'cidcidcidcidcidcidcidcid',
            "idList": "cidlcidlcidlcidlcidlcidl",
            'idShort': 1,
            'name': 'Card Name',
            'shortLink': 'cslcslss',
        },
        'cardSource': {
            'id': 'csidcsidcsidcsidcsidcsid',
            'idShort': 2,
            'name': 'Card Source Name',
            'shortLink': 'csslcssl'
        },
        "checkItem": {
            "id": "ciidciidciidciidciidciid",
            "name": "Check Item Name",
            "state": "complete",
            "textData": None
        },
        'checklist': {
            'id': 'clidclidclidclidclidclid',
            'name': 'Checklist Name'
        },
        'idMember': '51b9bca64517bd073d0031f5',
        'list': {
            'id': 'lidlidlidlidlidlidlidlid',
            'name': 'List Name'
        },
        "listAfter": {
            "id": "laidlaidlaidlaidlaidlaid",
            "name": "List After Name"
        },
        "listBefore": {
            "id": "lbidlbidlbidlbidlbidlbid",
            "name": "List Before Name"
        },
        'member': {
            'id': 'mcidmcidmcidmcidmcidmcid',
            'name': 'Member Creator Full Name', 
        },
        'old': {
            'due': NOW_DATETIME,
            'name': 'Old Name',
            'labelNames': {
                'red': 'Old Name label name'
            },
        },
        'organization': {
            'id': 'orgidorgidorgidorgidorgi',
            'name': 'Organization Name'
        },
        'text': 'Some data text that has a number of words in it.'
    },
    'date': NOW_DATETIME,
    'id': 'actidactidactidactidacti',
    'idMemberCreator': 'mcidmcidmcidmcidmcidmcid',
    'member': {
        'avatarHash': 'mahmahmahmahmahmahmahmahmahmahma',
        'fullName': 'Member Full Name',
        'id': 'midmidmidmidmidmidmidmid',
        'initials': 'MFN',
        'username': 'mfname'
    },
    'memberCreator': {
        'avatarHash': 'mcahmcahmcahmcahmcahmcahmcahmcah',
        'fullName': 'Member Creator Full Name', 
        'id': 'mcidmcidmcidmcidmcidmcid',
        'initials': 'MCFN',
        'username': 'mcfname'
    }
}


def sanitize(obj, replace_with=REPLACEMENTS):
    for k in obj:
        r = replace_with.get(k, None)
        if not r:
            continue
        v = obj[k]
        if (type(v) == dict or type(r) == dict) and (type(v) != type(r)):
            raise Exception('Mismatched types for key %s: %s vs %s' % (k, type(v), type(r)))
        if type(r) == dict:
            sanitize(v, r)
        else:
            obj[k] = r


for file_name in sys.argv[1:]:
    print 'processing', file_name

    with open(file_name) as f:
        json_dict = json.load(f)
    
    sanitize(json_dict)

    with open(file_name, 'w') as f:
        json.dump(json_dict, f, indent=2, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(',', ': '))

