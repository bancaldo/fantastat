import wx
import sys
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


OK = wx.OK | wx.ICON_EXCLAMATION
ACV = wx.ALIGN_CENTER_VERTICAL
ACH = wx.ALIGN_CENTER_HORIZONTAL | wx.ALL
YN = wx.YES_NO | wx.ICON_WARNING
DD = wx.CB_DROPDOWN
HS = wx.LB_HSCROLL


class ViewEvaluation(wx.Frame):
    def __init__(self, parent, title, is_editor=False):
        self.parent = parent
        self.title = title
        self.is_editor = is_editor

        super(ViewEvaluation, self).__init__(parent=self.parent, title=title)
        self.controller = self.parent.controller
        self.panel = PanelEvaluation(parent=self)
        self.panel.btn_delete.Disable()
        self.SetSize((350, 350))
        # bindings
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.panel.btn_save)
        self.Bind(wx.EVT_BUTTON, self.delete_evaluation, self.panel.btn_delete)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_save(self, event):
        """
        on_save(event) -> Call 'new_evaluation' controller method

        Callback bound to 'Save' button which saves new evaluation on database
        """
        code = self.panel.code.GetValue()
        fv = self.panel.fv.GetValue()
        v = self.panel.v.GetValue()
        cost = self.panel.cost.GetValue()
        day = self.panel.day.GetValue()
        if not code or not fv or not v or not cost or not day:
            self.show_message("WARNING: You have to fill all fields")
        else:
            if self.is_editor:
                self.controller.update_evaluation(code, fv, v, cost, day)
                self.show_message("Evaluation %s code %s updated!"
                                  % (day, code))
            else:
                self.controller.new_evaluation(code, fv, v, cost, day)
                self.show_message("New Evaluation %s code %s stored!"
                                  % (day, code))
            self.parent.on_refresh(None)
            # self.Destroy()

    # noinspection PyUnusedLocal
    def delete_evaluation(self, event):
        """
        delete_evaluation(event) -> Call 'delete_evaluation' controller method

        Callback bound to 'delete' button which deletes an evaluation from db
        """
        choice = wx.MessageBox('Deleting evaluation...are you sure?', 'warning',
                               wx.YES_NO | wx.ICON_WARNING)
        if choice == wx.YES:
            code = self.panel.code.GetValue()
            day = self.panel.day.GetValue()
            self.controller.delete_evaluation(int(code), day)
            self.show_message("Evaluation %s code %s deleted!" % (day, code))
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
        wx.MessageBox(string, 'core info', wx.OK | wx.ICON_EXCLAMATION)

    # noinspection PyUnusedLocal
    def on_quit(self, event):
        """
        on_quit(event) -> Call 'Destroy' frame method

        Callback bound to 'quit' button which destroys the frame and re-focus on
        main frame
        """
        self.parent.Enable()
        self.Destroy()


class PanelEvaluation(wx.Panel):
    def __init__(self, parent):
        super(PanelEvaluation, self).__init__(parent)
        # Attributes
        self.code = wx.TextCtrl(self)
        self.fv = wx.TextCtrl(self)
        self.v = wx.TextCtrl(self)
        self.cost = wx.TextCtrl(self)
        self.day = wx.TextCtrl(self)
        # Layout
        text_sizer = wx.FlexGridSizer(rows=6, cols=2, hgap=5, vgap=5)
        text_sizer.Add(wx.StaticText(self, label="Code:"), 0, ACV)
        text_sizer.Add(self.code, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="fv:"), 0, ACV)
        text_sizer.Add(self.fv, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="v:"), 0, ACV)
        text_sizer.Add(self.v, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="cost:"), 0, ACV)
        text_sizer.Add(self.cost, 0, wx.EXPAND)
        text_sizer.Add(wx.StaticText(self, label="day:"), 0, ACV)
        text_sizer.Add(self.day, 0, wx.EXPAND)
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


class ViewEvaluationSummary(wx.Frame):
    def __init__(self, parent, title):
        self.parent = parent
        super(ViewEvaluationSummary, self).__init__(parent=self.parent,
                                                    title=title)
        self.controller = self.parent.controller
        self.child = None
        self.panel = PanelEvaluationSummary(parent=self)
        self.SetSize((600, 600))

        self.Bind(wx.EVT_LIST_COL_CLICK, self.on_list_column,
                  self.panel.evaluation_list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_edit,
                  self.panel.evaluation_list)
        self.Bind(wx.EVT_CLOSE, self.on_quit)
        self.Bind(wx.EVT_BUTTON, self.on_quit, self.panel.btn_quit)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.panel.btn_refresh)
        self.Bind(wx.EVT_RADIOBOX, self.on_refresh, self.panel.rb_roles)
        self.Bind(wx.EVT_COMBOBOX, self.on_refresh, self.panel.cb_days)
        self.Centre()

    # noinspection PyUnusedLocal
    def on_refresh(self, event):
        """
        on_refresh(event) -> None

        Callback bound to 'refresh' button which refreshes values shown by
        list control
        """
        self.panel.evaluation_list.DeleteAllItems()
        role = self.panel.rb_roles.GetStringSelection()
        day = self.panel.cb_days.GetStringSelection()
        if day:
            evaluations = self.controller.get_evaluations(role=role, day=day)
            if evaluations:
                self.fill_evaluation_list(evaluations)
            else:
                self.show_message('No evaluations with day %s found!' % day)
        else:
            self.show_message('Please choose a Day to show')

    def fill_evaluation_list(self, evaluations):
        """
        fill_evaluation_list(evaluations) -> None

        It fills list control with evaluation values
        """
        for evaluation in evaluations:
            index = self.panel.evaluation_list.InsertItem(
                sys.maxint, str(evaluation.player.code))
            self.panel.evaluation_list.SetItem(
                index, 1, str(evaluation.player.name))
            self.panel.evaluation_list.SetItem(
                index, 2, str(evaluation.player.real_team))
            self.panel.evaluation_list.SetItem(
                index, 3, str(evaluation.fanta_vote))
            self.panel.evaluation_list.SetItem(
                index, 4, str(evaluation.vote))
            self.panel.evaluation_list.SetItem(
                index, 5, str(evaluation.cost))
            self.panel.evaluation_list.SetItem(
                index, 6, str(evaluation.day))

    # noinspection PyUnusedLocal
    def on_edit(self, event):
        """
        on_list(event) -> None

        Callback bound to 'list control' widget which opens the edit frame to
        update evaluation values when click on a list control row
        """
        code = event.GetItem().GetText()
        day = self.panel.cb_days.GetStringSelection()
        evaluation = self.controller.get_evaluation(int(code), int(day))
        self.controller.set_temporary_object(evaluation)
        role = self.panel.rb_roles.GetStringSelection()
        self.Disable()
        if not self.child:
            self.child = ViewEvaluation(self, "Edit Evaluation",
                                        is_editor=True)
            wx.CallAfter(self.child.Show)
            if evaluation:
                self.child.panel.code.ChangeValue(str(evaluation.player.code))
                self.child.panel.fv.ChangeValue(str(evaluation.fanta_vote))
                self.child.panel.v.ChangeValue(str(evaluation.vote))
                self.child.panel.cost.ChangeValue(str(evaluation.cost))
                self.child.panel.day.ChangeValue(str(evaluation.day))
                self.child.panel.btn_delete.Enable()
            else:
                self.show_message('No evaluation found')

    # noinspection PyUnusedLocal
    def on_list_column(self, event):
        """
        on_column(event) -> None

        Callback bound to 'list control' widget which sorts shown values by
        column value
        """
        role = self.panel.rb_roles.GetStringSelection()
        day = self.panel.cb_days.GetStringSelection()
        if day:
            self.panel.evaluation_list.DeleteAllItems()
            id_c = event.GetColumn()
            evaluations = self.controller.get_sorted_evaluations(id_c, role,
                                                                 day)
            if evaluations:
                self.fill_evaluation_list(evaluations)
            else:
                self.show_message('No evaluations found')
        else:
            self.show_message("Please choose a day")

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


class PanelEvaluationSummary(wx.Panel):
    def __init__(self, parent):
        super(PanelEvaluationSummary, self).__init__(parent=parent)
        roles = ('goalkeeper', 'defender', 'midfielder', 'forward')
        self.rb_roles = wx.RadioBox(self, -1, "roles", choices=roles,
                                    majorDimension=1, style=wx.RA_SPECIFY_COLS)
        days = parent.controller.get_days()
        self.cb_days = wx.ComboBox(self, -1, "", choices=days, style=DD)

        self.evaluation_list = AutoWidthListCtrl(self)
        self.evaluation_list.InsertColumn(0, 'code', wx.LIST_FORMAT_RIGHT, 75)
        self.evaluation_list.InsertColumn(1, 'name', width=150)
        self.evaluation_list.InsertColumn(2, 'team', width=50)
        self.evaluation_list.InsertColumn(3, 'fv', width=50)
        self.evaluation_list.InsertColumn(4, 'v', width=50)
        self.evaluation_list.InsertColumn(5, 'cost', width=50)
        self.evaluation_list.InsertColumn(6, 'day', width=50)

        evaluation_list_box = wx.BoxSizer(wx.HORIZONTAL)
        evaluation_list_box.Add(self.evaluation_list, 1, wx.EXPAND)
        btn_sizer = wx.FlexGridSizer(rows=1, cols=3, hgap=5, vgap=5)
        self.btn_quit = wx.Button(self, wx.ID_CANCEL, label="Quit")
        self.btn_refresh = wx.Button(self, wx.ID_OK, label="Refresh")
        btn_sizer.Add(self.btn_quit, 0, wx.EXPAND)
        btn_sizer.Add(self.btn_refresh, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.rb_roles, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.cb_days, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(evaluation_list_box, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(sizer)
