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
            url = ''
        return u'%s performed %s on [%s](%s)' % (
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
        url = attachment.get('url', '')
        return u'%s added [%s](%s) attachment to card [%s](%s)' % (
            a.creator_name(),
            attachment['name'],
            url,
            a.card_name(),
            a.card_url()
        )
    def addChecklistToCard(self, a):
        return u'%s added checklist **%s** to card [%s](%s)' % (
            a.creator_name(),
            a.data()['checklist']['name'],
            a.card_name(),
            a.card_url()
        )
    def addMemberToBoard(self, a):
        # Contains ['data']['idMemberAdded'] if we wanted to look it up
        return None
    def addMemberToCard(self, a):
        return u'%s added **%s** to card [%s](%s)' % (
            a.creator_name(),
            a['member']['fullName'],
            a.card_name(),
            a.card_url()
        )
    def addToOrganizationBoard(self, a):
        return u'%s added organization **%s** to board [%s](%s)' % (
            a.creator_name(),
            a.data()['organization']['name'],
            a.board_name(),
            a.board_url()
        )
    def copyCard(self, a):
        return u'%s copied card **%s** to [%s](%s)' % (
            a.creator_name(),
            a.data()['cardSource']['name'],
            a.card_name(),
            a.card_url()
        )
    def createBoard(self, a):
        return u'%s created board [%s](%s)' % (
            a.creator_name(),
            a.board_name(),
            a.board_url()
        )
    def createCard(self, a):
        return u'%s created card [%s](%s)' % (
            a.creator_name(),
            a.card_name(),
            a.card_url()
        )
    def createList(self, a):
        return u'%s created list **%s** on board [%s](%s)' % (
            a.creator_name(),
            a.data()['list']['name'],
            a.board_name(),
            a.board_url()
        )
    def commentCard(self, a):
        state = 'commented'
        if a.data().get('dateLastEdited', None) is not None:
            state = 'edited comment'
        return u'%s %s on card [%s](%s) \n>%s' % (
            a.creator_name(),
            state,
            a.card_name(),
            a.card_url(),
            a.data()['text'].replace('\n', '\n>')
        )
    def convertToCardFromCheckItem(self, a):
        return u'%s converted checklist item from **%s** to card [%s](%s)' % (
            a.creator_name(),
            a.data()['cardSource']['name'],
            a.card_name(),
            a.card_url()
        )
    def deleteAttachmentFromCard(self, a):
        return u'%s deleted attachment **%s** from card [%s](%s)' % (
            a.creator_name(),
            a.data()['attachment']['name'],
            a.card_name(),
            a.card_url()
        )
    def deleteCard(self, a):
        return u'%s deleted card from list **%s** on board [%s](%s)' % (
            a.creator_name(),
            a.data()['list']['name'],
            a.board_name(),
            a.board_url()
        )
    def makeAdminOfBoard(self, a):
        return u'%s made **%s** an admin of board [%s](%s)' % (
            a.creator_name(),
            a['member']['fullName'],
            a.board_name(),
            a.board_url()
        )
    def makeNormalMemberOfBoard(self, a):
        return u'%s made **%s** a member of board [%s](%s)' % (
            a.creator_name(),
            a['member']['fullName'],
            a.board_name(),
            a.board_url()
        )
    def moveCardToBoard(self, a):
        # Handled in paired action moveCardFromBoard
        return None
    def moveCardFromBoard(self, a):
        return u'%s moved card [%s](%s) from **%s** to **%s**' % (
            a.creator_name(),
            a.card_name(),
            a.card_url(),
            a.board_name(),
            a.data()['boardTarget']['name']
        )
    def moveListToBoard(self, a):
        # Handled in paired action moveListFromBoard
        return None
    def moveListFromBoard(self, a):
        return u'%s moved list **%s** from **%s** to **%s**' % (
            a.creator_name(),
            a.data()['list']['name'],
            a.board_name(),
            a.data()['boardTarget']['name']
        )
    def removeChecklistFromCard(self, a):
        return u'%s removed checklist **%s** from card [%s](%s)' % (
            a.creator_name(),
            a.data()['checklist']['name'],
            a.card_name(),
            a.card_url()
        )
    def removeMemberFromCard(self, a):
        return u'%s removed **%s** from card [%s](%s)' % (
            a.creator_name(),
            a['member']['fullName'],
            a.card_name(),
            a.card_url()
        )
    def unconfirmedBoardInvitation(self, a):
        return u'%s invited (unconfirmed) **%s** to board [%s](%s)' % (
            a.creator_name(),
            a.data()['member']['name'],
            a.board_name(),
            a.board_url()
        )
    def updateBoard(self, a):
        # Many possibilities, signified through contents of a.data()['old']
        old = a.data()['old']
        name = old.get('name', None)
        if name is not None:
            return u'%s renamed from **%s** to **%s**' % (
                a.creator_name(),
                name,
                a.board_name()
            )
        label_names = old.get('labelNames', None)
        if label_names is not None:
            new_names = a.data()['board']['labelNames']
            label_desc = []
            for k,v in new_names.iteritems():
                label_desc.append('%s to **%s**' % (k, v))
            label_desc = ', '.join(label_desc)
            return u'%s changed label %s on board [%s](%s)' % (
                a.creator_name(),
                label_desc,
                a.board_name(),
                a.board_url()
            )
        prefs = old.get('prefs', None)
        if prefs is not None:
            pref_name = None
            if prefs.get('voting', None) is not None:
                pref_name = 'voting'
            elif prefs.get('comments', None) is not None:
                pref_name = 'comments'
            elif prefs.get('selfJoin', None) is not None:
                pref_name = 'selfJoin'
            if pref_name is not None:
                return u'%s set **%s** preference to **%s** on board [%s](%s)' % (
                    a.creator_name(),
                    pref_name,
                    a.data()['board']['prefs'][pref_name],
                    a.board_name(),
                    a.board_url()
                )
        return self._unknown_action(a)
    def updateCard(self, a):
        # Many possibilities, signified through contents of a.data()['old']
        old = a.data()['old']
        id_list = old.get('idList', None)
        if id_list is not None:
            return u'%s moved card [%s](%s) from **%s** to **%s**' % (
                a.creator_name(),
                a.card_name(),
                a.card_url(),
                a.data()['listBefore']['name'],
                a.data()['listAfter']['name']
            )
        closed = old.get('closed', None)
        if closed is not None:
            new_state = a.data()['card']['closed'] and 'archived' or 're-opened'
            return u'%s %s card [%s](%s)' % (
                a.creator_name(),
                new_state,
                a.card_name(),
                a.card_url()
            )
        name = old.get('name', None)
        if name is not None:
            return u'%s renamed card from **%s** to [%s](%s)' % (
                a.creator_name(),
                name,
                a.card_name(),
                a.card_url()
            )
        desc = old.get('desc', None)
        if desc is not None:
            # Note: new description is not included
            return u'%s updated description for card [%s](%s)' % (
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
            return u'%s %s card [%s](%s)' % (
                a.creator_name(),
                state,
                a.card_name(),
                a.card_url()
            )
        if old.get('pos', None) is not None:
            # Always accompanies a list move, so just ignore
            return None
        if old.get('idAttachmentCover', None) is not None:
            # No useful info
            return None
        return self._unknown_action(a)
    def updateCheckItemStateOnCard(self, a):
        checked_state = 'checked'
        if a.data()['checkItem']['state'] == 'incomplete':
            checked_state = 'unchecked'
        return u'%s %s **%s** on card [%s](%s)' % (
            a.creator_name(),
            checked_state,
            a.data()['checkItem']['name'],
            a.card_name(),
            a.card_url()
        )
    def updateChecklist(self, a):
        old = a.data()['old']
        name = old.get('name', None)
        if name is not None:
            card_desc = ''
            if a.has_card_name():
                card_desc = ' on card [%s](%s)' % (a.card_name(), a.card_url())
            return u'%s renamed checklist from **%s** to **%s**%s' % (
                a.creator_name(),
                name,
                a.data()['checklist']['name'],
                card_desc
            )
        return self._unknown_action(a)

