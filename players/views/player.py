import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from players.views.styles import OK, ACV, YN, DD


class ViewPlayer(wx.Frame):
    def __init__(self, parent, title, is_editor=False):
        self.parent = parent
        self.title = title
        self.is_editor = is_editor
        super(ViewPlayer, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        self.panel = PanelPlayer(parent=self)
        self.panel.btn_delete.Disable()
        self.SetSize((350, 250))
        # bindings
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.panel.btn_save)
        self.Bind(wx.EVT_BUTTON, self.delete_player, self.panel.btn_delete)
        if self.is_editor:
            self.panel.btn_delete.Enable()
        self.Centre()

    # noinspection PyUnusedLocal
    def on_save(self, event):
        """
        on_save(event) -> Call 'new_player' controller method

        Callback bound to 'Save' button which saves new player on database
        """
        code = self.panel.code.GetValue()
        name = self.panel.name.GetValue()
        if not code:
            self.show_message("WARNING: You have to fill 'code' field")
        elif not name:
            self.show_message("WARNING: You have to fill 'name' field")
        else:
            real_team = self.panel.real_team.GetValue()
            role = self.panel.role.GetValue()
            cost = self.panel.cost.GetValue()
            if self.is_editor:
                self.controller.update_player(code, name, real_team, role, cost)
                self.show_message("Player %s [%s] updated!" % (name, code))
            else:
                self.controller.new_player(code, name, real_team, role, cost)
                self.show_message("New Player %s [%s] stored!" % (name, code))
            self.parent.Enable()
            self.parent.on_refresh(None)
            self.Destroy()

    # noinspection PyUnusedLocal
    def delete_player(self, event):
        """
        delete_player(event) -> Call 'delete_player' controller method

        Callback bound to 'delete' button which deletes a player from db
        Player Evaluations will be deleted by cascade attribute set
        in models.
        """
        choice = wx.MessageBox('Deleting player...are you sure?', 'warning', YN)
        if choice == wx.YES:
            code = self.panel.code.GetValue()
            self.controller.delete_player(int(code))
            self.show_message("Player [%s] deleted!" % code)
            self.parent.Enable()
            self.parent.on_refresh(None)
            self.Destroy()
        else:
            choice.Destroy()

    def clear_text_controls(self):
        """
        clear_text_controls() -> None

        It clears all TextControl widgets
        """
        for w in [w for w in self.panel.GetChildren()
                  if isinstance(w, wx.TextCtrl)]:
            w.SetValue('')

    @staticmethod
    def show_message(string):
        """
        show_message(string) -> MessageBox

        It shows a message box with string as message.
        """
        wx.MessageBox(string, 'core info', OK)

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        """
        on_quit(event) -> Call 'Destroy' frame method

        Callback bound to 'quit' button which destroys the frame and re-focus on
        main frame
        """
        self.parent.Enable()
        self.Destroy()


class PanelPlayer(wx.Panel):
    def __init__(self, parent):
        super(PanelPlayer, self).__init__(parent)
        # Attributes
        self.code = wx.TextCtrl(self)
        self.name = wx.TextCtrl(self)
        self.real_team = wx.TextCtrl(self)
        roles = ('goalkeeper', 'defender', 'midfielder', 'forward')
        self.role = wx.ComboBox(self, -1, "", choices=roles, style=DD)
        self.cost = wx.TextCtrl(self)
        # Layout
        text_sizer = wx.FlexGridSizer(rows=5, cols=2, hgap=5, vgap=5)
        text_sizer.Add(wx.StaticText(self, label="Player Code:"), 0, ACV)
        text_sizer.Add(self.code, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="Player Name:"), 0, ACV)
        text_sizer.Add(self.name, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="team:"), 0, ACV)
        text_sizer.Add(self.real_team, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="role:"), 0, ACV)
        text_sizer.Add(self.role, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="cost:"), 0, ACV)
        text_sizer.Add(self.cost, 0, wx.EXPAND)
        text_sizer.AddGrowableCol(1)
        # Sizers
        button_sizer = wx.FlexGridSizer(rows=1, cols=3, hgap=5, vgap=5)
        self.btn_save = wx.Button(self, wx.ID_SAVE)
        self.btn_delete = wx.Button(self, wx.ID_DELETE)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_quit.SetDefault()
        button_sizer.Add(self.btn_save, 0, ACV)
        button_sizer.Add(self.btn_delete, 0, ACV)
        button_sizer.Add(self.btn_quit, 0, ACV)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetBackgroundColour('LightGray')
        self.SetSizer(sizer)


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class ViewPlayerSummary(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super(ViewPlayerSummary, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        self.child = None
        self.panel = PanelPlayerSummary(parent=self)
        self.SetSize((600, 600))

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_edit,
                  self.panel.player_list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_list_column,
                  self.panel.player_list)
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)
        self.Bind(wx.EVT_RADIOBOX, self.on_refresh, self.panel.rb_roles)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        """
        on_quit(event) -> Call 'Destroy' frame method

        Callback bound to 'quit' button which destroys the frame and re-focus on
        main frame
        """
        self.parent.Enable()
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        """
        on_refresh(event) -> None

        Callback bound to 'refresh' button which refreshes values shown by
        list control
        """
        self.panel.player_list.DeleteAllItems()
        role = self.panel.rb_roles.GetStringSelection()
        players = self.controller.get_players_by_role(role)
        if players:
            self.fill_player_list(players)
        else:
            self.show_message('No players found')

    def fill_player_list(self, players):
        """
        fill_player_list(players) -> None

        It fills list control with player values
        """
        for player in players:
            index = self.panel.player_list.InsertItem(10000, str(player.code))
            self.panel.player_list.SetItem(index, 1, str(player.name))
            self.panel.player_list.SetItem(index, 2, str(player.real_team))
            self.panel.player_list.SetItem(index, 3, str(player.role))
            self.panel.player_list.SetItem(index, 4, str(player.cost))

    # noinspection PyUnusedLocal
    def on_edit(self, event):
        """
        on_list(event) -> None

        Callback bound to 'list control' widget which opens the edit frame to
        update player values when click on a list control row
        """
        code = event.GetItem().GetText()
        player = self.controller.get_player_by_code(code)
        role = self.panel.rb_roles.GetStringSelection()
        self.controller.set_temporary_object(player)
        self.Disable()
        if not self.child:
            self.child = ViewPlayer(self, "Edit Player", is_editor=True)
            wx.CallAfter(self.child.Show)
            if player:
                self.child.panel.code.ChangeValue(str(player.code))
                self.child.panel.name.ChangeValue(str(player.name))
                self.child.panel.real_team.ChangeValue(str(player.real_team))
                self.child.panel.role.ChangeValue(str(player.role))
                self.child.panel.cost.ChangeValue(str(player.cost))
            else:
                self.show_message('No player found')

    # noinspection PyUnusedLocal
    def on_list_column(self, event):
        """
        on_column(event) -> None

        Callback bound to 'list control' widget which sorts shown values by
        column value
        """
        role = self.panel.rb_roles.GetStringSelection()
        self.panel.player_list.DeleteAllItems()
        id_column = event.GetColumn()
        if id_column == 4:
            players = self.controller.get_sorted_players_by_cost(role)
        else:
            players = self.controller.get_sorted_players(id_column, role)
        if players:
            self.fill_player_list(players)
        else:
            self.show_message('No players found')

    @staticmethod
    def show_message(string):
        """
        show_message(string) -> MessageBox

        It shows a message box with string as message.
        """
        wx.MessageBox(string, 'core info', wx.OK | wx.ICON_EXCLAMATION)


class PanelPlayerSummary(wx.Panel):
    def __init__(self, parent):
        super(PanelPlayerSummary, self).__init__(parent=parent)
        roles = ('goalkeeper', 'defender', 'midfielder', 'forward')
        self.rb_roles = wx.RadioBox(self, -1, "roles", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_COLS)
        self.player_list = AutoWidthListCtrl(self)
        self.player_list.InsertColumn(0, 'code', wx.LIST_FORMAT_RIGHT, 75)
        self.player_list.InsertColumn(1, 'name', width=150)
        self.player_list.InsertColumn(2, 'team', width=50)
        self.player_list.InsertColumn(3, 'role', width=125)
        self.player_list.InsertColumn(4, 'cost', width=50)

        player_list_box = wx.BoxSizer(wx.HORIZONTAL)
        player_list_box.Add(self.player_list, 1, wx.EXPAND)
        btn_sizer = wx.FlexGridSizer(rows=1, cols=3, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="Refresh")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rb_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(player_list_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
