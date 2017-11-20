import wx
import sys
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


FRAME = wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
OK = wx.OK | wx.ICON_EXCLAMATION
ACV = wx.ALIGN_CENTER_VERTICAL
ACH = wx.ALIGN_CENTER_HORIZONTAL | wx.ALL
YN = wx.YES_NO | wx.ICON_WARNING
DD = wx.CB_DROPDOWN
HS = wx.LB_HSCROLL


class ViewPlayer(wx.Frame):
    def __init__(self, parent, title, is_editor=False):
        self.parent = parent
        self.title = title
        self.is_editor = is_editor
        super(ViewPlayer, self).__init__(parent=self.parent, title=title,
                                         style=FRAME)
        self.controller = self.parent.controller
        self.panel = PanelPlayer(parent=self)
        self.panel.btn_delete.Disable()
        self.SetSize((350, 250))
        # bindings
        self.Bind(wx.EVT_BUTTON, self.parent.quit_subframe, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.panel.btn_save)
        self.Bind(wx.EVT_BUTTON, self.delete_player, self.panel.btn_delete)
        if self.is_editor:
            self.panel.btn_delete.Enable()

        self.parent.show_subframe(self)  # Show and center the frame

    # noinspection PyUnusedLocal
    def on_save(self, event):
        """
        on_save(event) -> Call 'new_player' controller method

        Callback bound to 'Save' button wich saves new player on database
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
            self.controller.new_player(code, name, real_team, role)
            self.clear_text_controls()

    # noinspection PyUnusedLocal
    def delete_player(self, event):
        """
        delete_player(event) -> Call 'delete_player' controller method

        Callback bound to 'delete' button wich deletes a player from db
        Player Evaluations will be deleted by cascade attribute set
        in models.
        """
        choice = wx.MessageBox('Deleting player...are you sure?', 'warning',
                               wx.YES_NO | wx.ICON_WARNING)
        if choice == wx.YES:
            code = self.panel.code.GetValue()
            self.controller.delete_player(int(code))
            self.clear_text_controls()
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

    # noinspection PyUnusedLocal
    def update_player(self, event):
        """
        update_player(event) -> Call 'update_player' controller method

        Callback bound to 'Save' button wich updates player values after
        user modifies them in the edit frame.
        Edit frame is invoked when listcontrol is clicked by user
        """
        code = self.panel.code.GetValue()
        name = self.panel.name.GetValue()
        real_team = self.panel.real_team.GetValue()
        role = self.panel.role.GetValue()
        cost = self.panel.cost.GetValue()
        if code and name:
            player = self.controller.update_player(code, name, real_team,
                                                   role, cost)
            self.clear_text_controls()
            self.show_message("INFO: player %s updated" % code)
        else:
            self.show_message("ERROR: Missing fields, please fill them")
        self.Destroy()

    @staticmethod
    def show_message(string):
        """
        show_message(string) -> MessageBox

        It shows a message box with string as message.
        """
        wx.MessageBox(string, 'core info', wx.OK | wx.ICON_EXCLAMATION)


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
        button_sizer.Add(self.btn_save, 0, wx.ALIGN_CENTER_VERTICAL)
        button_sizer.Add(self.btn_delete, 0, wx.ALIGN_CENTER_VERTICAL)
        button_sizer.Add(self.btn_quit, 0, wx.ALIGN_CENTER_VERTICAL)
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
        super(ViewPlayerSummary, self).__init__(parent=self.parent, title=title,
                                                style=FRAME)
        self.controller = self.parent.controller
        self.panel = PanelPlayerSummary(parent=self)
        self.SetSize((600, 400))

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list,
                  self.panel.player_list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_list_column,
                  self.panel.player_list)
        self.Bind(wx.EVT_BUTTON, self.parent.quit_subframe, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)
        self.Bind(wx.EVT_RADIOBOX, self.on_refresh, self.panel.rb_roles)

        self.parent.show_subframe(self)  # Show and center the frame

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        """
        on_quit(event) -> Call 'Destroy' frame method

        Callback bound to 'quit' button which destroys the frame
        """
        self.Destroy()

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        """
        on_refresh(event) -> None

        Callback bound to 'refresh' button wich refreshes values shown by
        listcontrol
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

        It fills listcontrol with player values
        """
        for player in players:
            index = self.panel.player_list.InsertStringItem(sys.maxint,
                                                            str(player.code))
            self.panel.player_list.SetStringItem(index, 1, str(player.name))
            self.panel.player_list.SetStringItem(index, 2,
                                                 str(player.real_team))
            self.panel.player_list.SetStringItem(index, 3, str(player.role))
            self.panel.player_list.SetStringItem(index, 4, str(player.cost))

    # noinspection PyUnusedLocal
    def on_list(self, event):
        """
        on_list(event) -> None

        Callback bound to 'listcontrol' widget wich opens the edit frame to
        update player values when click on a listcontrol row
        """
        role = self.panel.rb_roles.GetStringSelection()
        item_id = event.m_itemIndex
        code = self.panel.player_list.GetItemText(item_id)
        player = self.controller.get_player_by_code(int(code))
        if player:
            self.controller.set_temporary_object(player)
            view_edit = ViewPlayer(self.parent, "Edit Player", is_editor=True)
            view_edit.panel.code.SetValue(str(player.code))
            view_edit.panel.name.SetValue(player.name)
            view_edit.panel.real_team.SetValue(player.real_team)
            view_edit.panel.role.ChangeValue(player.role)
            view_edit.panel.cost.ChangeValue(str(player.cost))
            view_edit.SetWindowStyle(wx.STAY_ON_TOP)
        else:
            self.show_message('No player with code %s found' % code)

    # noinspection PyUnusedLocal
    def on_list_column(self, event):
        """
        on_column(event) -> None

        Callback bound to 'listcontrol' widget wich sorts shown values by
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
        btn_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="Refresh")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rb_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(player_list_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
