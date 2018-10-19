import os
import re
import wx
from model import Model
from players.views.core import Core
from django.db.utils import OperationalError


class Controller(object):
    def __init__(self):
        app = wx.App()
        self.model = Model()
        self.view = Core(parent=None, controller=self, title='Players')
        self.d_evaluations = {}
        self.d_avg = {}
        self.init_view()
        app.MainLoop()

    def init_view(self):
        """
        init_view()

        It initializes the frame widgets activating or deactivating
        radio boxes and menus
        """
        try:
            players = self.get_players()
            if players:
                self.view.m_players_import.Enable(False)
                self.enable_widgets(True)
                evaluations = self.get_evaluations(day=1, role='goalkeeper')
                if evaluations:
                    self.get_players_avg()
                    self.view.fill_players(players)
                    self.view.set_status_text("Found %s players on db" %
                                              len(players))
                else:
                    self.view.show_message(
                        'No data to show, please import evaluations!')
                    self.view.m_ev_import.Enable(True)
            else:
                self.enable_widgets(False)
                self.view.show_message(
                    'No players on database yet, please import them!')
                self.view.m_ev_import.Enable(False)
        except OperationalError:
            self.view.show_message("Database not found. Please use \n"
                                   "'python manage.py makemigrations players'\n"
                                   "and 'python manage.py migrate' commands")

    def enable_widgets(self, enable=True):
        """
        enable_widgets(boolean)

        Enable or disable radio button and refresh button
        """
        if not enable:
            self.view.panel.rb_roles.Disable()
            self.view.panel.btn_refresh.Disable()
        else:
            self.view.panel.rb_roles.Enable()
            self.view.panel.btn_refresh.Enable()

    def set_temporary_object(self, obj):
        """
        set_temporary_object(obj)

        It stores object to a temporary attribute to get later when
        the user will update the object
        """
        self.model.set_temporary_object(obj)

    def get_temporary_object(self):
        """
        get_temporary_object() -> object

        It returns the object stored in the temporary attribute
        """
        return self.model.get_temporary_object()

    def set_day(self, value):
        """
        set_day(int)

        It sets the day attribute to integer passed as argument.
        Day is the day number of evaluation file
        """
        self.model.set_day(value)

    def get_day(self):
        """
        get_day() -> int

        It returns the day attribute.
        Day is the day number of evaluation file the user is importing
        """
        return self.model.get_day()

    def get_players(self):
        """
        get_players() -> iterable

        Return a list of all players present in database
        """
        return self.model.get_players()

    def get_players_by_role(self, role):
        """
        get_players_by_role(role) -> list of Players

        It returns a list of Player objects filtered by role
        """
        return self.model.get_players_by_role(role)

    def new_player(self, code, name, real_team, role, cost):
        """
        new_player(code, name, real_team, role, cost) -> Player object

        it creates a new player object
        """
        self.model.new_player(code, name, real_team, role, cost)

    def import_players(self, path):
        """
        import_players(path)

        it imports players on database from txt file
        """
        self.model.clear_bulk_players()
        with open(path) as f:
            data = [line.strip() for line in f.readlines()]
        self.view.set_status_text("importing players")
        print "INFO: importing players..."
        count = 1
        players_dict = self.model.get_players_data()
        self.view.set_range(len(data))
        # string sample: 100|NAME|ROM|6.5|6.5|19
        for s in data:
            code, name, real_team, fv, v, cost = s.strip().split('|')
            role = self.get_role(code)
            if code not in players_dict.keys():
                self.import_player_bulk(code, name, real_team, role, cost)
            else:
                player_data = players_dict.get(int(code))
                if name != player_data[0] or real_team != player_data[1]:
                    self.update_player(code, name, real_team, role, cost)
            self.view.set_status_text("importing data %s/%s"
                                      % (count, len(data)))
            self.view.set_progress(count)
            self.view.Update()
            count += 1
        self.commit_all_players()
        print "INFO: Success!"
        self.view.show_message('Players successfully imported!')
        self.view.set_progress(0)  # clear gauge
        self.show_data()

    def show_data(self):
        """
        show_data()

        it shows the data in list control
        """
        evs = self.get_evaluations(day=1, role='goalkeeper')
        if not evs:
            self.view.show_message('No evaluations found, please import them!')
            self.view.set_status_text('No evaluations in database')
            self.view.m_ev_import.Enable(True)
        else:
            players = self.get_players()
            self.view.fill_players(players)

    def import_evaluations(self, path):
        """
        import_evaluations(path)

        it imports evaluations on database from txt file
        """
        self.model.clear_bulk_evaluations()
        players = self.get_players()
        if not players:
            self.view.show_message('No players found, import them before')
        else:
            day = self.get_day_from_path(path)
            if day:
                with open(path) as f:
                    data = [line.strip() for line in f.readlines()]
                print "INFO: importing evaluations..."
                self.view.set_range(len(data))
                count = 1
                # string sample: 100|NAME|ROM|6.5|6.5|19
                day_evs = self.get_evaluations(day=day, role='goalkeeper')
                if day_evs:
                    self.delete_day_evaluations(day)
                    print "INFO: Deleting all evaluations of day %s..." % day

                for s in data:
                    code, name, real_team, fv, v, cost = s.strip().split('|')
                    code = code.replace("\xef\xbb\xbf", "")
                    cost = cost.replace("\xc2\xa0", "") # avoid Non-breaking sp.
                    player = self.get_player_by_code(int(code))
                    if not player:
                        role = self.get_role(code)
                        self.new_player(code, name, real_team, role, cost)
                        print "INFO: new player %s stored!" % code

                    self.import_ev_bulk(code, fv, v, cost, day)
                    self.view.set_status_text("importing data %s/%s"
                                              % (count, len(data)))
                    self.view.set_progress(count)
                    self.view.Update()
                    count += 1
                self.commit_all_evaluations()
                self.get_players_avg()
                print "INFO: Success!"
                self.view.show_message('Evaluations successfully imported!')
                self.view.set_progress(0)  # clear gauge
                self.init_view()

    def get_player_by_code(self, code):
        """
        get_player_by_code(code) -> Player object

        it returns a Player object with code=code
        """
        return self.model.get_player_by_code(code)

    def delete_player(self, code):
        """
        delete_player(code)

        It deletes player with code=code
        """
        return self.model.delete_player(code)

    def delete_all_data(self):
        """
        delete_all_data()

        It deletes all the players and all the evaluations stored in database
        """
        self.model.delete_all_players()
        self.model.delete_all_evaluations()

    def delete_evaluation(self, code, day):
        """
        delete_evaluation(code, day)

        It deletes the evaluation of day=day and player.code=code
        """
        self.model.delete_evaluation(code, day)

    def delete_day_evaluations(self, day):
        """
        delete_day_evaluations(day)

        It deletes all the evaluations stored in database with day=day
        """
        self.model.delete_day_evaluations(day)
        print "INFO: all evaluations with day %s deleted!" % day

    def commit_all_players(self):
        """
        commit_all_players()

        It creates all objects in bulk_players_to_create list at a time
        with only a commit operation
        """
        self.model.import_all_players()

    def commit_all_evaluations(self):
        """
        commit_all_evaluations()

        It creates all objects in bulk_evaluations_to_create list at a time
        with only a commit operation
        """
        self.model.import_all_evaluations()

    def import_player_bulk(self, code, name, real_team, role, cost):
        """
        import_player_bulk(code, name, real_team, role, cost)

        It adds a new Player object to bulk_players_to_create list
        """
        self.model.add_new_player_to_bulk(code, name, real_team, role, cost)

    def import_ev_bulk(self, code, fv, v, cost, day):
        """
        import_ev_bulk(code, fv, v, cost, day)

        It adds a new Evaluation object to bulk_evaluations_to_create list
        """
        self.model.add_new_ev_to_bulk(code, fv, v, cost, day)

    def get_sorted_players(self, id_c, role):
        """
        get_sorted_players(id_c, role) -> list of Players

        It returns a list of Player objects filtered by role and
        sorted by id_column id_c
        """
        if id_c > 2:
            return self.get_players_ordered_by_avg(id_c, role)
        columns = {0: 'code', 1: 'name', 2: 'real_team'}
        return self.model.get_players_ordered_by_filter(columns.get(id_c), role)

    def get_sorted_players_by_cost(self, role):
        """
        get_sorted_players_by_cost(role) -> list of Players

        It returns a list of Player objects sorted by 'cost'
        """
        return self.model.get_players_ordered_by_filter('-cost', role)

    def get_players_ordered_by_avg(self, id_c, role):
        """
        get_players_ordered_by_avg(id_c, role) -> list of Players

        It returns a list of Player objects filtered by 'role' and sorted by
        descendant field value
        """
        columns = {3: 0, 4: 1, 5: 2}
        players = self.get_players_by_role(role)
        if id_c == 6:
            return sorted(players,
                          key=lambda x: int(self.d_avg.get(
                              x.code)[-1].split(' ')[0]), reverse=True)
        return sorted(players,
                      key=lambda x: self.d_avg.get(x.code)[columns.get(id_c)],
                      reverse=True)

    def update_player(self, code, name, real_team, role, cost):
        """
        update_player(code, name, real_team, role, cost) -> Player object

        It updates Player values and return Player object
        """
        self.model.update_player(code, name, real_team, role, cost)

    def update_evaluation(self, code, fv, v, cost, day):
        """
        update_evaluation(code, fv, v, cost, day) -> Evaluation object

        It updates Evaluation values and return Evaluation object
        """
        self.model.update_evaluation(code, fv, v, cost, day)

    def new_evaluation(self, code, fv, v, cost, day):
        """
        new_evaluation(code, fv, v, cost, day)

        it creates a new evaluation object
        """
        if not self.get_player_by_code(int(code)):
            self.view.show_message("You must create player with code %s before"
                                   % code)
        else:
            self.model.new_evaluation(code, fv, v, cost, day)

    def get_evaluation(self, code, day):
        """
        get_evaluation(code, day) -> Evaluation object

        It returns a the Evaluation object with code=code and day=day
        """
        return self.model.get_evaluation(code, day)

    def get_days(self):
        """
        get_days() -> iterable

        It returns the list of the imported days
        """
        return [str(day) for day in self.model.get_days()]

    @staticmethod
    def get_role(code):
        """
        get_role(code) -> string

        It returns the string of role by player code passed as argument
        """
        if int(code) < 200:
            return "goalkeeper"
        elif 200 <= int(code) < 500:
            return "defender"
        elif 500 <= int(code) < 800:
            return "midfielder"
        elif int(code) >= 800:
            return "forward"
        else:
            raise AttributeError('Not a Int input')

    def get_evaluations(self, role, day):
        """
        get_evaluations(day, role=None) -> Evaluation list

        it returns a list of all Evaluation objects with day=day and
        Player role=role
        """
        return self.model.get_evaluations(role=role, day=day)

    def get_sorted_evaluations(self, id_c, role, day):
        """
        get_sorted_evaluations(id_c, role, day) -> list of Evaluations

        It returns a list of Evaluation objects filtered by role, day and
        sorted by id_column id_c
        """
        columns = {0: 'player__code', 1: 'player__name', 2: 'player__real_team',
                   3: '-fanta_vote', 4: '-vote', 5: '-cost'}
        return self.model.get_evaluations_ordered_by_filter(columns.get(id_c),
                                                            role, int(day))

    def get_players_avg(self):
        """
        get_players_avg() -> dictionary

        It returns a dictionary with format player.code: (*avg_values)
        *avg_values are:
        fv_avg: avg of player.fanta_vote
        v_avg: avg of player.vote
        rate: rate evaluated match / played match
        cost_indicator: the difference between the actual player cost
                        ed the initial one
        """
        days = self.model.get_days()
        played = len(days)
        print "INFO: days played -> %s" % played
        last_day = self.model.get_last_imported_day()
        players = self.model.get_players()
        count = 1
        self.view.set_range(len(players))
        for player in players:
#            fv_avg = self.model.get_avg(player=player, field='fanta_vote')
#            v_avg = self.model.get_avg(player=player, field='vote')
            fv_avg = self.model.get_v_avg(player=player, fanta=True)
            v_avg = self.model.get_v_avg(player=player, fanta=False)
            evaluated = self.model.get_evaluated(player)
            rate = 100 * evaluated / float(played)
            ev = self.model.get_evaluation(code=player.code, day=last_day)
            if ev:
                last_cost = ev.cost
                delta_cost = last_cost - player.cost
                s_cost = '(%s)' % delta_cost
                if delta_cost > 0:
                    s_cost = '(+%s)' % delta_cost
                cost_indicator = '%s %s' % (last_cost, s_cost)
            else:
                cost_indicator = '%s (-)' % player.cost
            self.d_avg[player.code] = (fv_avg, v_avg, rate, cost_indicator)
            self.view.set_progress(count)
            count += 1
            self.view.set_status_text("calculating data %s/%s"
                                      % (count, len(players)))
            self.view.Update()
        self.view.set_progress(0)  # clear gauge
        return self.d_avg

    def get_avg_dict(self):
        """
        get_avg_dict() -> dictionary

        it returns the d_avg attribute with all avg values of players
        """
        return self.d_avg

    def get_day_from_path(self, path):
        """
        get_day_from_path() -> int

        it returns the day number extract from path.
        If file name hasn't got a day it shows an error message.
        Filename must be in format 'MCCnn.txt'.
        """
        try:
            day = re.findall(r'\d+', os.path.normpath(path))[-1]
            return int(day)
        except IndexError:
            self.view.show_message("Invalid filename! "
                                   "Name must contain at least a number")

    def generate_html(self, iterable):
        table_header = '''
        <table bgcolor="#FFFFF" border="2">
          <tr bgcolor="66CCCC" >
            <td align=center><B>codice</B></td>
            <td align=center width=120><B>Giocatore</B></td>
            <td align=center width=40><B>squadra</B></td>
            <td align=center width=60><B>media FV</B></td>
            <td align=center width=60><B>media V</B></td>
            <td align=center width=60><B>affidabilita'</B></td>
            <td align=center width=60><B>valutazione</B></td>
          </tr>
        '''
        self.html.write(table_header)
        filtered = [(k, self.d_avg.get(k)) for k in iterable]
        # metto in ordine, prima per presenze, poi per fanta media
        sorted_players = sorted(filtered, key=lambda x: (x[1][2], x[1][0]), 
                                reverse=True)
        for record in sorted_players:
            key, data = record
            player = self.get_player_by_code(int(key))
            fv_avg, v_avg, rate, cost = data
            row = '''
            <tr>
              <td align=center>%s</td>
              <td width=120>%s</td>
              <td align=center>%s</td>
              <td width=60 align=center>%s</td>
              <td width=60 align=center>%s</td>
              <td width=60 align=center>%s</td>
              <td width=60 align=center>%s</td>
            </tr>''' % (key, player.name, player.real_team, 
                        round(float(fv_avg), 3), round(float(v_avg), 3), 
                        round(float(rate), 3), cost)
            self.html.write(row)
        self.html.write('</table>')

    def build_report(self):
        players_dict = self.get_avg_dict()
        gk = [key for key in players_dict if key < 200]
        df = [key for key in players_dict if 200 < key < 500]
        mf = [key for key in players_dict if 500 < key < 800]
        fw = [key for key in players_dict if key > 800]
        html_name = "players_stat.html"
        self.html = open(html_name, "w")
        for role, players in [("Portieri", gk), ("Difensori", df), 
                              ("Centrocampisti", mf), ("Attaccanti", fw)]:
            print "INFO: generating %s report..." % role
            self.html.write("<br><strong>%s</strong><br>" % role)
            self.generate_html(players)
            print "INFO: report %s successfully created!" % role
        self.html.close()
        print "INFO: file <%s> successfully created!" % html_name




