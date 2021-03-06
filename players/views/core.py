import os
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from players.views.player import ViewPlayer, ViewPlayerSummary
from players.views.evaluation import ViewEvaluation, ViewEvaluationSummary
from players.views.styles import OK


class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)


class Core(wx.Frame):
    def __init__(self, parent, controller, title):
        super(Core, self).__init__(parent=parent, title=title)
        self.parent = parent
        self.controller = controller
        self.panel = PanelCore(self)
        self.panel.SetBackgroundColour('LightGray')
        self.status_bar = self.CreateStatusBar(2)
        self.status_bar.SetStatusWidths([200, -1])
        gauge_pos, gauge_size = self.get_gauge_dimensions()
        self.gauge = wx.Gauge(self.status_bar, -1, 100, gauge_pos, gauge_size)

        # Menus
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        # Player menu
        m_player = wx.Menu()
        self.menubar.Append(m_player, "Players")
        self.m_new_player = m_player.Append(200, "New Player", "New Player")
        self.m_players_summary = m_player.Append(201, "Summary", "Summary")
        self.m_stat = m_player.Append(202, "Statistic", "Statistic")
        m_ev = wx.Menu()
        self.menubar.Append(m_ev, "Evaluations")
        self.m_new_ev = m_ev.Append(203, "New Evaluation", "New Evaluation")
        self.m_ev_summary = m_ev.Append(204, "Summary", "Summary")
        m_import = wx.Menu()
        self.menubar.Append(m_import, "Import")
        self.m_ev_import = m_import.Append(205, "import evaluations",
                                           "import evaluations")
        self.m_players_import = m_import.Append(206, "import players",
                                                "import players")
        m_reset = wx.Menu()
        self.menubar.Append(m_reset, "Reset")
        self.m_delete = m_reset.Append(207, "Delete all data",
                                       "Delete all data")

        # Bindings
        # player bindings
        self.Bind(wx.EVT_RADIOBOX, self.on_refresh, self.panel.rb_roles)
        self.Bind(wx.EVT_MENU, self.new_player, self.m_new_player)
        self.Bind(wx.EVT_MENU, self.on_import_player, self.m_players_import)
        self.Bind(wx.EVT_MENU, self.on_players_summary, self.m_players_summary)
        self.Bind(wx.EVT_MENU, self.on_statistic, self.m_stat)
        self.Bind(wx.EVT_MENU, self.new_evaluation, self.m_new_ev)
        self.Bind(wx.EVT_MENU, self.on_import_evaluation, self.m_ev_import)
        self.Bind(wx.EVT_MENU, self.on_evs_summary, self.m_ev_summary)
        self.Bind(wx.EVT_MENU, self.on_delete_data, self.m_delete)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_list_column,
                  self.panel.players)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_edit,
                  self.panel.players)
        self.Bind(wx.EVT_SIZE, self.on_size)
        size = (600, 600)
        self.SetSize(size)
        self.Centre()
        self.Show()

    # Core Frame methods
    def get_gauge_dimensions(self):
        """
        get_gauge_dimensions(self) -> tuple_a, tuple_b

        tuple_a is a tuple with x position and y position of seconf field
        of the StatusBar
        """
        pos_x, pos_y, dim_x, dim_y = self.status_bar.GetFieldRect(1)
        return (pos_x, pos_y), (dim_x, dim_y)

    def on_size(self, event):
        """
        on_size()

        it redraws the gauge rectangle and repositions when frame windows is
        resized
        """
        size = self.GetSize()
        self.SetSize(size)
        gauge_pos, gauge_size = self.get_gauge_dimensions()
        self.gauge.SetSize(gauge_size)
        event.Skip()
        self.Update()

    def set_range(self, value):
        """
        set_range(value)

        It sets the maximum value of gauge widget
        """
        self.gauge.SetRange(value)

    def set_progress(self, value):
        """
        set_progress(value)

        It sets the actual progress value to gauge widget
        """
        self.gauge.SetValue(value)

    def set_status_text(self, value):
        """
        set_status_text(value)

        It sets the text to the first field of StatusBar
        """
        self.status_bar.SetStatusText(value)

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

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        """
        on_refresh(event) -> None

        Callback bound to 'refresh' button wich refreshes values shown by
        list control
        """
        role = self.panel.rb_roles.GetStringSelection()
        self.panel.players.DeleteAllItems()
        players = self.controller.get_players_by_role(role)
        if players:
            self.set_status_text("%s players found" % len(players))
            self.fill_players(players)
        else:
            self.set_status_text('No players found')

    def on_list_column(self, event):
        """
        on_column(event) -> None

        Callback bound to 'list_control' widget wich sorts shown values by
        column value
        """
        role = self.panel.rb_roles.GetStringSelection()
        self.panel.players.DeleteAllItems()
        id_column = event.GetColumn()
        players = self.controller.get_sorted_players(id_column, role)
        if players:
            self.fill_players(players)
        else:
            self.set_status_text('No players found')

    def fill_players(self, players):
        """
        fill_players(players) -> None

        It fills list_control with player values and relatives avg values
        """
        avg_data = self.controller.get_avg_dict()
        for player in players:
            try:
                avg_fv, avg_v, rate, d_cost = avg_data.get(player.code)
            except TypeError:
                self.set_status_text('No data to show')
            except ValueError:
                self.set_status_text(
                    'Invalid file format: file strings must be:'
                    '\n nnn|NAME|TEAM|n.n|n.n|n')
            else:
                index = self.panel.players.InsertItem(10000, str(player.code))
                self.panel.players.SetItem(index, 1, str(player.name))
                self.panel.players.SetItem(index, 2, str(player.real_team))
                self.panel.players.SetItem(index, 3, str(avg_fv))
                self.panel.players.SetItem(index, 4, str(avg_v))
                self.panel.players.SetItem(index, 5, str(rate))
                self.panel.players.SetItem(index, 6, str(d_cost))

    # Player section
    # noinspection PyUnusedLocal
    def new_player(self, event):
        """
        new_player(event) -> None

        Callback bound to the 'new player' menu. It opens a frame
        to save a new player on database
        """
        self.Disable()
        child = ViewPlayer(parent=self, title='New Player')
        wx.CallAfter(child.Show)

    # noinspection PyUnusedLocal
    def on_players_summary(self, event):
        """
        on_players_summary(event) -> None

        Callback bound to the 'summary' player menu. It opens a frame
        to show the players summary
        """
        self.Disable()
        players = self.controller.get_players()
        if players:
            child = ViewPlayerSummary(parent=self, title='Players Summary')
            wx.CallAfter(child.Show)
            child.fill_player_list(players)
        else:
            self.show_message("No players in database, please import them")

    # noinspection PyUnusedLocal
    def on_statistic(self, event):
        """
        on_statistic(event) -> None

        Callback bound to the 'statistic' player menu. It builds a html-report
        with all player statistics
        """
        self.controller.build_report()

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
            self.set_status_text('All data deleted!')
            self.m_ev_import.Enable(False)
            self.m_players_import.Enable(True)

    # noinspection PyUnusedLocal
    def on_import_player(self, event):
        """
        on_import_player(event) -> None

        Callback bound to the 'import players' menu. It opens a file browser
        to choose the standard MCCnn.txt players file
        """
        input_file = self.get_file(extension="txt")
        if input_file:
            self.controller.import_players(input_file)
            self.m_players_import.Enable(False)
        else:
            self.set_status_text('No file selected!')

    # Evaluation section
    # noinspection PyUnusedLocal
    def on_import_evaluation(self, event):
        """
        on_import_evaluation(event) -> None

        Callback bound to the 'import evaluations' menu. It opens a file browser
        to choose the standard MCCnn.txt evaluations file
        """
        input_file = self.get_file(extension="txt")
        if input_file:
            self.controller.import_evaluations(input_file)
        else:
            self.set_status_text('No file selected!')

    # noinspection PyUnusedLocal
    def new_evaluation(self, event):
        """
        new_evaluation(event) -> None

        Callback bound to the 'new evaluation' menu. It opens a frame
        to save a new evaluation on database
        """
        self.Disable()
        child = ViewEvaluation(parent=self, title='New Evaluation')
        wx.CallAfter(child.Show)

    # noinspection PyUnusedLocal
    def on_evs_summary(self, event):
        """
        on_evs_summary(event) -> None

        Callback bound to the 'summary' evaluation menu. It opens a frame
        to show the evaluations summary
        """
        self.Disable()
        days = self.controller.get_days()
        if days:
            child = ViewEvaluationSummary(parent=self,
                                          title='Evaluations Summary')
            wx.CallAfter(child.Show)
        else:
            self.show_message("No evaluations in database, please import them")

    # noinspection PyUnusedLocal
    def on_edit(self, event):
        """
        on_list(event) -> None

        Callback bound to 'list_control' widget wich opens the edit frame to
        update player values when click on a listcontrol row
        """
        self.Disable()
        code = event.GetItem().GetText()
        player = self.controller.get_player_by_code(code)
        self.controller.set_temporary_object(player)
        child = ViewPlayer(self, "Edit player", is_editor=True)
        wx.CallAfter(child.Show)
        if player:
            child.panel.code.ChangeValue(str(player.code))
            child.panel.name.ChangeValue(str(player.name))
            child.panel.real_team.ChangeValue(str(player.real_team))
            child.panel.role.ChangeValue(str(player.role))
            child.panel.cost.ChangeValue(str(player.cost))
        else:
            self.set_status_text('No player found')

    # noinspection PyUnusedLocal
    def get_file(self, extension="txt"):
        """
        get_file() -> path

        Call wx.FileDialog to open txt file
        """
        ext = "(*.%s)|*.%s|" % (extension, extension)
        input_file = ""
        wildcard = "Evaluations File %s" "All files (*.*)|*.*" % ext
        browser = wx.FileDialog(parent=self, message='Open file',
                                defaultDir=os.getcwd(), wildcard=wildcard,
                                style=wx.FD_OPEN)
        if browser.ShowModal() == wx.ID_OK:
            input_file = browser.GetPath()
        browser.Destroy()
        return input_file


class PanelCore(wx.Panel):
    def __init__(self, parent):
        super(PanelCore, self).__init__(parent=parent)

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
        btn_sizer = wx.FlexGridSizer(rows=1, cols=3, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="Refresh")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rb_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(players_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
