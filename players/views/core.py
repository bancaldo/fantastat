import os
import sys
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from player import ViewPlayer, ViewPlayerSummary
from evaluation import ViewEvaluation, ViewEvaluationSummary


OK = wx.OK | wx.ICON_EXCLAMATION
ACV = wx.ALIGN_CENTER_VERTICAL
STYLE = wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | \
    wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class Core(wx.Frame):
    def __init__(self, parent, controller, title):
        super(Core, self).__init__(parent=parent, title=title)
        self.parent = parent
        self.controller = controller
        self.sub_view = None
        self.panel = PanelCore(self)
        self.panel.SetBackgroundColour('LightGray')
        # Menues
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        # Player menu
        m_player = wx.Menu()
        self.menubar.Append(m_player, "Players")
        self.m_new_player = m_player.Append(-1, "New Player", "New Player")
        self.m_players_summary = m_player.Append(-1, "Summary", "Summary")
        m_ev = wx.Menu()
        self.menubar.Append(m_ev, "Evaluations")
        self.m_new_ev = m_ev.Append(-1, "New Evaluation", "New Evaluation")
        self.m_ev_summary = m_ev.Append(-1, "Summary", "Summary")
        m_import = wx.Menu()
        self.menubar.Append(m_import, "Import")
        self.m_ev_import = m_import.Append(-1, "import evaluations",
                                           "import evaluations")
        self.m_players_import = m_import.Append(-1, "import players",
                                                "import players")
        m_reset = wx.Menu()
        self.menubar.Append(m_reset, "Reset")
        self.m_delete = m_reset.Append(-1, "Delete all data", "Delete all data")

        # Bindings
        # player bindings
        self.Bind(wx.EVT_RADIOBOX, self.on_refresh, self.panel.rb_roles)
        self.Bind(wx.EVT_MENU, self.new_player, self.m_new_player)
        self.Bind(wx.EVT_MENU, self.on_import_player, self.m_players_import)
        self.Bind(wx.EVT_MENU, self.on_players_summary, self.m_players_summary)
        self.Bind(wx.EVT_MENU, self.new_evaluation, self.m_new_ev)
        self.Bind(wx.EVT_MENU, self.on_import_evaluation, self.m_ev_import)
        self.Bind(wx.EVT_MENU, self.on_evs_summary, self.m_ev_summary)
        self.Bind(wx.EVT_MENU, self.on_delete_data, self.m_delete)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_list_column,
                  self.panel.players)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_list, self.panel.players)

        size = (600, 600)
        self.SetSize(size)
        self.Show()

    # Core Frame methods
    # noinspection PyUnusedLocal
    def on_quit(self, event):
        """
        on_quit(event) -> Call 'Destroy' frame method

        Callback bound to 'quit' button which destroys the frame
        """
        self.Destroy()

    @staticmethod
    def show_message(string):
        """
        show_message(string) -> MessageBox

        It shows a message box with string as message.
        """
        wx.MessageBox(string, 'core info', OK)

    @staticmethod
    def show_subframe(child):
        """
        show_subframe(widget) -> None

        It shows the widget subframe in a centred position
        """
        child.Centre()
        child.Show()

    # noinspection PyUnusedLocal
    def quit_subframe(self, event):
        """
        quit_subframe(event) -> None

        It quits the subframe and enables the parent frame
        """
        subframe = event.GetEventObject().GetParent()
        if isinstance(subframe, wx.Panel):
            subframe = subframe.GetParent()
        self.Enable()
        subframe.Destroy()

    def set_progress(self, count):
        """
        set_progress(count) -> None

        It sets count value to progress bar and wait for 5 micro seconds
        """
        self.panel.status.set_progress(count)
        self.panel.status.SetLabel('elaborating %s' % count)
        wx.MicroSleep(5)

    def set_range(self, max_limit):
        """
        set_range(max_limit) -> None

        It sets the max range limit to progress bar
        """
        self.panel.status.set_range(max_limit)

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        """
        on_refresh(event) -> None

        Callback bound to 'refresh' button wich refreshes values shown by
        listcontrol
        """
        role = self.panel.rb_roles.GetStringSelection()
        self.panel.players.DeleteAllItems()
        players = self.controller.get_players_by_role(role)
        if players:
            self.fill_players(players)
        else:
            self.panel.status.SetLabel('No players found')

    def on_list_column(self, event):
        """
        on_column(event) -> None

        Callback bound to 'listcontrol' widget wich sorts shown values by
        column value
        """
        role = self.panel.rb_roles.GetStringSelection()
        self.panel.players.DeleteAllItems()
        id_column = event.GetColumn()
        players = self.controller.get_sorted_players(id_column, role)
        if players:
            self.fill_players(players)
        else:
            self.panel.status.SetLabel('No players found')

    def fill_players(self, players):
        """
        fill_players(players) -> None

        It fills listcontrol with player values and relatives avg values
        """
        avg_data = self.controller.get_avg_dict()
        for player in players:
            try:
                avg_fv, avg_v, rate, d_cost = avg_data.get(player.code)
            except TypeError:
                self.panel.status.SetLabel('No data to show')
            except ValueError:
                self.panel.status.SetLabel(
                    'Invalid file format: file strings must be:'
                    '\n nnn|NAME|TEAM|n.n|n.n|n')
            else:
                index = self.panel.players.InsertStringItem(sys.maxint,
                                                            str(player.code))
                self.panel.players.SetStringItem(index, 1, str(player.name))
                self.panel.players.SetStringItem(index, 2,
                                                 str(player.real_team))
                self.panel.players.SetStringItem(index, 3, str(avg_fv))
                self.panel.players.SetStringItem(index, 4, str(avg_v))
                self.panel.players.SetStringItem(index, 5, str(rate))
                self.panel.players.SetStringItem(index, 6, str(d_cost))

    # Player section
    # noinspection PyUnusedLocal
    def new_player(self, event):
        """
        new_player(event) -> None

        Callback bound to the 'new player' menu. It opens a frame
        to save a new player on database
        """
        self.Disable()
        ViewPlayer(parent=self, title='New Player')

    # noinspection PyUnusedLocal
    def on_players_summary(self, event):
        """
        on_players_summary(event) -> None

        Callback bound to the 'summary' player menu. It opens a frame
        to show the players summary
        """
        players = self.controller.get_players()
        if players:
            self.Disable()
            summary = ViewPlayerSummary(parent=self, title='Players Summary')
            summary.fill_player_list(players)
        else:
            self.show_message("No players in database, please import them")

    # noinspection PyUnusedLocal
    def on_delete_data(self, event):
        """
        on_delete_data(event) -> None

        Callback bound to the 'Delete all data' reset menu. It deletes all data!
        """
        choice = wx.MessageBox('Deleting All Players and evaluations?',
                               'warning', wx.YES_NO | wx.ICON_WARNING)
        if choice == wx.YES:
            self.controller.delete_all_data()
            self.panel.players.DeleteAllItems()
            self.panel.status.SetLabel('All data deleted!')
            self.m_ev_import.Enable(False)
            self.m_players_import.Enable(True)

    # noinspection PyUnusedLocal
    def on_import_player(self, event):
        """
        on_import_player(event) -> None

        Callback bound to the 'import players' menu. It opens a file browser
        to choose the standard MCCnn.txt players file
        """
        path = FileBrowser(self).GetPath()
        if path:
            self.controller.import_players(path)
            self.m_players_import.Enable(False)
        else:
            self.panel.status.SetLabel('No file selected!')

    # Evaluation section
    # noinspection PyUnusedLocal
    def on_import_evaluation(self, event):
        """
        on_import_evaluation(event) -> None

        Callback bound to the 'import evaluations' menu. It opens a file browser
        to choose the standard MCCnn.txt evaluations file
        """
        path = FileBrowser(self).GetPath()
        if path:
            self.controller.import_evaluations(path)
        else:
            self.panel.status.SetLabel('No file selected!')

    # noinspection PyUnusedLocal
    def new_evaluation(self, event):
        """
        new_evaluation(event) -> None

        Callback bound to the 'new evaluation' menu. It opens a frame
        to save a new evaluation on database
        """
        self.Disable()
        ViewEvaluation(parent=self, title='New Evaluation')
    
    # noinspection PyUnusedLocal
    def on_evs_summary(self, event):
        """
        on_evs_summary(event) -> None

        Callback bound to the 'summary' evaluation menu. It opens a frame
        to show the evaluations summary
        """
        days = self.controller.get_days()
        if days:
            self.Disable()
            s = ViewEvaluationSummary(parent=self, title='Evaluations Summary')
        else:
            self.show_message("No evaluations in database, please import them")

    # noinspection PyUnusedLocal
    def on_list(self, event):
        """
        on_list(event) -> None

        Callback bound to 'listcontrol' widget wich opens the edit frame to
        update player values when click on a listcontrol row
        """
        item_id = event.m_itemIndex
        player_code = self.panel.players.GetItemText(item_id)
        player = self.controller.get_player_by_code(player_code)
        if player:
            self.controller.set_temporary_object(player)
            view_edit = ViewPlayer(self, "Edit player", is_editor=True)
            view_edit.panel.code.SetValue(str(player_code))
            view_edit.panel.name.SetValue(player.name)
            view_edit.panel.real_team.SetValue(player.real_team)
            view_edit.panel.role.SetValue(player.role)
            view_edit.panel.cost.SetValue(str(player.cost))
            view_edit.SetWindowStyle(wx.STAY_ON_TOP)
        else:
            self.panel.status.SetLabel('No player with code %s found'
                                       % player_code)


class PanelCore(wx.Panel):
    def __init__(self, parent):
        super(PanelCore, self).__init__(parent=parent)
        self.status = ProgressStatusBar(self)

        roles = ('goalkeeper', 'defender', 'midfielder', 'forward')
        self.rb_roles = wx.RadioBox(self, -1, "role", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_COLS)

        self.players = AutoWidthListCtrl(self)
        self.players.InsertColumn(0, 'code', wx.LIST_FORMAT_RIGHT, 50)
        self.players.InsertColumn(1, 'name', width=125)
        self.players.InsertColumn(2, 'real team', width=50)
        self.players.InsertColumn(3, 'dfv', width=50)
        self.players.InsertColumn(4, 'dv', width=50)
        self.players.InsertColumn(5, 'rate', width=50)
        self.players.InsertColumn(6, 'cost', width=50)

        players_box = wx.BoxSizer(wx.HORIZONTAL)
        players_box.Add(self.players, 1, wx.EXPAND)

        btn_sizer = wx.FlexGridSizer(rows=1, cols=2, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="Refresh")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rb_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(players_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.status, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)


class ProgressStatusBar(wx.StatusBar):
    """Custom StatusBar with a built-in progress bar"""
    def __init__(self, parent, id_=wx.ID_ANY, style=wx.SB_FLAT,
                 name='ProgressStatusBar'):
        super(ProgressStatusBar, self).__init__(parent, id_, style, name)
        self._changed = False
        self.busy = False
        self.timer = wx.Timer(self)
        self.progress_bar = wx.Gauge(self, style=wx.GA_HORIZONTAL)
        self.progress_bar.Hide()

        self.SetFieldsCount(2)
        self.SetStatusWidths([-1, 155])
        # self.SetBackgroundColour('Pink')

        self.Bind(wx.EVT_IDLE, lambda evt: self.__reposition())
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def __del__(self):
        if self.timer.IsRunning():
            self.timer.Stop()

    def __reposition(self):
        """Repositions the gauge as necessary"""
        if self._changed:
            field = self.GetFieldsCount() - 1
            rect = self.GetFieldRect(field)
            progress_bar_pos = (rect.x + 2, rect.y + 2)
            self.progress_bar.SetPosition(progress_bar_pos)
            progress_bar_size = (rect.width - 8, rect.height - 4)
            self.progress_bar.SetSize(progress_bar_size)
        self._changed = False

    # noinspection PyUnusedLocal
    def on_size(self, evt):
        self._changed = True
        self.__reposition()
        evt.Skip()

    # noinspection PyUnusedLocal
    def on_timer(self, evt):
        if not self.progress_bar.IsShown():
            self.timer.Stop()
        if self.busy:
            self.progress_bar.Pulse()

    def run(self, rate=100):
        if not self.timer.IsRunning():
            self.timer.Start(rate)

    def get_progress(self):
        return self.progress_bar.GetValue()

    def set_progress(self, val):
        if not self.progress_bar.IsShown():
            self.show_progress(True)

        if val == self.progress_bar.GetRange():
            self.progress_bar.SetValue(0)
            self.show_progress(False)
        else:
            self.progress_bar.SetValue(val)

    def set_range(self, val):
        if val != self.progress_bar.GetRange():
            self.progress_bar.SetRange(val)

    def show_progress(self, show=True):
        self.__reposition()
        self.progress_bar.Show(show)

    def start_busy(self, rate=100):
        self.busy = True
        self.__reposition()
        self.show_progress(True)
        if not self.timer.IsRunning():
            self.timer.Start(rate)

    def stop_busy(self):
        self.timer.Stop()
        self.show_progress(False)
        self.progress_bar.SetValue(0)
        self.busy = False

    def is_busy(self):
        return self.busy


class FileBrowser(wx.FileDialog):
    def __init__(self, parent, ddir=os.getcwd()):
        wildcard = "File Evaluations (*.txt)|*.txt|" "Tutti i files (*.*)|*.*"
        super(FileBrowser, self).__init__(parent=parent, message='',
                                          defaultDir=ddir,
                                          wildcard=wildcard, style=wx.OPEN)
        self.ShowModal()
