class ActionPrinter(object):
    #
    # Helpers
    #
    def get_message(self, action):
        t = action.type()
        handler = getattr(self, t, None)
        if handler is None:
            handler = self._unknown_action
        msg = handler(action)
        return msg
    def _unknown_action(self, a):
        if a.has_card_name():
            name = a.card_name()
            url = a.card_url()
        elif a.has_board_name():
            name = a.board_name()
            url = a.board_url()
        else:
            name = '<unknown name>'
            url = '<unknown url>'
        return '%s performed %s on [%s](%s)' % (
            a.creator_name(),
            a.type(),
            name,
            url
        )
    #
    # Methods map directly to action name and used for lookup.
    # No direct documentation, but list of names here:
    # https://trello.com/docs/api/board/index.html
    #
    def addAttachmentToCard(self, a):
        attachment = a.data()['attachment']
        return '%s added [%s](%s) attachment to card [%s](%s)' % (
            a.creator_name(),
            attachment['name'],
            attachment['url'],
            a.card_name(),
            a.card_url()
        )
    def addChecklistToCard(self, a):
        return '%s added checklist **%s** to card [%s](%s)' % (
            a.creator_name(),
            a.data()['checklist']['name'],
            a.card_name(),
            a.card_url()
        )
    def addMemberToBoard(self, a):
        # Contains ['data']['idMemberAdded'] if we wanted to look it up
        return None
    def addMemberToCard(self, a):
        return '%s added **%s** to card [%s](%s)' % (
            a.creator_name(),
            a['member']['fullName'],
            a.card_name(),
            a.card_url()
        )
    def createBoard(self, a):
        return '%s created board [%s](%s)' % (
            a.creator_name(),
            a.board_name(),
            a.board_url()
        )
    def createCard(self, a):
        return '%s created card [%s](%s)' % (
            a.creator_name(),
            a.card_name(),
            a.card_url()
        )
    def createList(self, a):
        return '%s created list **%s** on board [%s](%s)' % (
            a.creator_name(),
            a.data()['list']['name'],
            a.board_name(),
            a.board_url()
        )
    def commentCard(self, a):
        state = 'commented'
        if a.data().get('dateLastEdited', None) is not None:
            state = 'edited comment'
        return '%s %s on card [%s](%s) \n>%s' % (
            a.creator_name(),
            state,
            a.card_name(),
            a.card_url(),
            a.data()['text'].replace('\n', '\n>')
        )
    def moveCardToBoard(self, a):
        # Any card move is also going to trigger a moveCardFromBoard
        # event, which will report what we want.
        pass
    def moveCardFromBoard(self, a):
        return '%s moved card [%s](%s) from **%s** to **%s**' % (
            a.creator_name(),
            a.card_name(),
            a.card_url(),
            a.board_name(),
            a.data()['boardTarget']['name']
        )
    def removeMemberFromCard(self, a):
        return '%s removed **%s** from card [%s](%s)' % (
            a.creator_name(),
            a['member']['fullName'],
            a.card_name(),
            a.card_url()
        )
    def updateBoard(self, a):
        # Many possibilities, signified through contents of a.data()['old']
        old = a.data()['old']
        name = old.get('name', None)
        if name is not None:
            return '%s renamed from **%s** to **%s**' % (
                a.creator_name(),
                name,
                a.board_name()
            )
        return self._unknown_action(a)
    def updateCard(self, a):
        # Many possibilities, signified through contents of a.data()['old']
        old = a.data()['old']
        id_list = old.get('idList', None)
        if id_list is not None:
            return '%s moved card [%s](%s) from **%s** to **%s**' % (
                a.creator_name(),
                a.card_name(),
                a.card_url(),
                a.data()['listBefore']['name'],
                a.data()['listAfter']['name']
            )
        closed = old.get('closed', None)
        if closed is not None:
            new_state = a.data()['card']['closed'] and 'archived' or 're-opened'
            return '%s %s card [%s](%s)' % (
                a.creator_name(),
                new_state,
                a.card_name(),
                a.card_url()
            )
        name = old.get('name', None)
        if name is not None:
            return '%s renamed card from **%s** to [%s](%s)' % (
                a.creator_name(),
                name,
                a.card_name(),
                a.card_url()
            )
        desc = old.get('desc', None)
        if desc is not None:
            # Note: new description is not included
            return '%s updated description for card [%s](%s)' % (
                a.creator_name(),
                a.card_name(),
                a.card_url()
            )
        due = old.get('due', False)
        if due is not False:
            new_due = a.data()['card']['due']
            state = 'added due date **%s** to' % (new_due,)
            if new_due is None:
                state = 'removed due date from'
            return '%s %s card [%s](%s)' % (
                a.creator_name(),
                state,
                a.card_name(),
                a.card_url()
            )
        pos = old.get('pos', None)
        if pos is not None:
            # Always accompanies a list move, so just ignore
            return None
        return self._unknown_action(a)
    def updateCheckItemStateOnCard(self, a):
        checked_state = 'checked'
        if a.data()['checkItem']['state'] == 'incomplete':
            checked_state = 'unchecked'
        return '%s %s  **%s** on card [%s](%s)' % (
            a.creator_name(),
            checked_state,
            a.data()['checkItem']['name'],
            a.card_name(),
            a.card_url()
        )

