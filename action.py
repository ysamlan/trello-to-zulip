"""Wraps an action json object"""
class Action(object):
    def __init__(self, json):
        self.json = json
    def __getitem__(self, key):
        return self.json[key]
    def type(self):
        return self.json['type']
    def date(self):
        return self.json['date']
    def data(self):
        return self.json['data']
    def board_name(self):
        return self.data()['board']['name']
    def has_board_name(self):
        data = self.data()
        return ('board' in data) and ('name' in data['board'])
    def has_card_name(self):
        data = self.data()
        return ('card' in data) and ('name' in data['card'])
    def card_name(self):
        return self.data()['card']['name']
    def board_url(self):
        board = self.data()['board']
        return 'https://trello.com/board/%s' % (board['id'],)
    def card_url(self):
        card = self.data()['card']
        return 'https://trello.com/c/%s' % (card['id'],)
    def creator_name(self):
        member = self.json.get('memberCreator', None)
        if member is None:
            return '<unknown>'
        return member['fullName']
    def derive_subject(self):
        subject = '<unknown>'
        if self.has_card_name():
            subject = self.card_name()
        elif self.has_board_name():
            subject = self.board_name()
        return shorten_subject(subject)


ZULIP_SUBJECT_MAX   = 60

def shorten_subject(s):
    if len(s) > ZULIP_SUBJECT_MAX:
        return s[:ZULIP_SUBJECT_MAX - 3] + '...'
    return s

