from models import Player, Evaluation
from django.db.models import Avg, Max


class Model(object):
    def __init__(self):
        super(Model, self).__init__()
        self.temporary_object = None
        self.bulk_players_to_create = []
        self.bulk_evaluations_to_create = []
        self.day = 1

    def set_temporary_object(self, obj):
        """
        set_temporary_object(obj)

        It stores the object passed as argument to get later
        """
        print "INFO: Set temporary object to %s" % obj
        self.temporary_object = obj

    def get_temporary_object(self):
        """
        get_temporary_object() -> temporary object

        It returns the temporary object stored previously
        """
        print "INFO: Retrieve temporary object %s" % self.temporary_object
        return self.temporary_object

    def set_day(self, value):
        """
        set_day(int)

        Set day attribute to value
        """
        self.day = int(value)

    def get_day(self):
        """
        get_day() -> int

        it returns the value of day attribute
        """
        return self.day

    @staticmethod
    def new_player(code, name, real_team, role, cost):
        """
        new_player(code, name, real_team, role, cost) -> Player object

        it creates a new player object
        """
        player = Player.objects.create(code=int(code),
                                       name=name.upper(),
                                       real_team=real_team.upper(),
                                       role=role.lower(), cost=int(cost))
        return player

    def get_players_data(self):
        """
        get_players_data() -> dictionary

        it returns a dictionary in format with couple key: value
        player.code: (player.name, player.real_team)
        """
        return {p.code: (p.name, p.real_team) for p in self.get_players()}

    @staticmethod
    def get_player_by_code(code):
        """
        get_player_by_code(code) -> Player object

        it returns a Player object with code=code
        """
        return Player.objects.filter(code=int(code)).first()

    @staticmethod
    def get_players():
        """
        get_players() -> iterable

        Return a list of all players present in database
        """
        return Player.objects.order_by('code').all()

    def import_all_players(self):
        """
        import_all_players()

        It creates all objects in bulk_players_to_create list at a time
        with only a commit operation
        """
        Player.objects.bulk_create(self.bulk_players_to_create)

    def clear_bulk_players(self):
        """
        clear_bulk_players()

        It clears bulk_players_to_create list
        """
        self.bulk_players_to_create = []

    @staticmethod
    def get_players_count():
        """
        get_players_count() -> int

        It returns the number of players stored in database
        """
        return Player.objects.count()

    @staticmethod
    def delete_all_players():
        """
        delete_all_players()

        It deletes all the players stored in database
        """
        Player.objects.all().delete()

    def delete_player(self, code):
        """
        delete_player(code)

        It deletes player with code=code
        """
        player = self.get_player_by_code(int(code))
        if player:
            player.delete()

    def add_new_player_to_bulk(self, code, name, real_team, role, cost):
        """
        add_new_player_to_bulk(code, name, real_team, role, cost)

        It adds a new Player object to bulk_players_to_create list
        """
        player = Player(code=int(code), name=u'%s' % name.upper(),
                        real_team=real_team, role=role.lower(), cost=int(cost))
        self.bulk_players_to_create.append(player)

    @staticmethod
    def get_players_ordered_by_filter(filter_name, role):
        """
        get_players_ordered_by_filter(filter_name, role) -> list of Players

        It returns a list of Player objects filtered by role and
        sorted by filter_name
        """
        return Player.objects.filter(role=role.lower()).order_by(
            filter_name).all()

    @staticmethod
    def get_players_by_role(role):
        """
        get_players_by_role(role) -> list of Players

        It returns a list of Player objects filtered by role
        """
        return Player.objects.filter(role=role.lower()).order_by('code').all()

    def update_player(self, code, name, real_team, role, cost):
        """
        update_player(code, name, real_team, role, cost) -> Player object

        It updates Player values and return Player object
        """
        player = self.get_player_by_code(int(code))
        if not player:
            player = self.get_temporary_object()
        player.code = int(code)
        player.name = name.upper()
        player.real_team = real_team.upper()
        player.role = role.lower()
        player.cost = int(cost)
        player.save()
        print "INFO: Player %s updated!" % name
        return player

    def new_evaluation(self, code, fv, v, cost, day):
        """
        new_evaluation(code, fv, v, cost, day) -> Evaluation object

        it creates a new evaluation object
        """
        player = self.get_player_by_code(int(code))
        if player:
            ev = Evaluation.objects.create(fanta_vote=float(fv),
                                           vote=float(v), cost=int(cost),
                                           player=player, day=int(day))
            return ev

    @staticmethod
    def get_evaluations(day, role=None):
        """
        get_evaluations(day, role=None) -> Evaluation list

        it returns a list of all Evaluation objects with day=day and
        Player role=role
        """
        if role:
            return Evaluation.objects.filter(
                player__role=role.lower(),
                day=int(day)).order_by('player__code').all()
        return Evaluation.objects.filter(
            day=int(day)).order_by('player__code').all()

    def get_evaluation(self, code, day):
        """
        get_evaluation(code, day) -> Evaluation object

        It returns a the Evaluation object with code=code and day=day
        """
        player = self.get_player_by_code(int(code))
        return Evaluation.objects.filter(player=player, day=int(day)).first()

    @staticmethod
    def get_evaluations_ordered_by_filter(filter_name, role, day):
        """
        get_evaluations_ordered_by_filter(filter_name, role, day)
            -> list of Evaluations

        It returns a list of Evaluation objects filtered by role, day and
        sorted by filter_name
        """
        return Evaluation.objects.filter(player__role=role.lower(),
                                         day=day).order_by(filter_name).all()

    def update_evaluation(self, code, fv, v, cost, day):
        """
        update_evaluation(code, fv, v, cost, day) -> Evaluation object

        It updates Evaluation values and return Evaluation object
        """
        ev = self.get_evaluation(int(code), day)
        if not ev:
            ev = self.get_temporary_object()
        ev.fanta_vote = fv
        ev.vote = v
        ev.cost = cost
        ev.save()
        return ev

    def add_new_ev_to_bulk(self, code, fv, v, cost, day):
        """
        add_new_ev_to_bulk(code, fv, v, cost, day)

        It adds a new Evaluation object to bulk_evaluations_to_create list
        """
        player = self.get_player_by_code(int(code))
        ev = Evaluation(fanta_vote=float(fv), vote=float(v),
                        cost=int(cost), day=int(day), player=player)
        self.bulk_evaluations_to_create.append(ev)

    @staticmethod
    def get_days():
        """
        get_days() -> iterable

        It returns the list of the imported days
        """
        return [ev['day'] for ev in
                Evaluation.objects.order_by('day').values('day').distinct()]

    @staticmethod
    def delete_day_evaluations(day):
        """
        delete_day_evaluations(day)

        It deletes all the evaluations stored in database with day=day
        """
        Evaluation.objects.filter(day=int(day)).all().delete()

    @staticmethod
    def delete_evaluation(code, day):
        """
        delete_evaluation(code, day)

        It deletes the evaluation of day=day and player.code=code
        """
        Evaluation.objects.filter(player__code=int(code),
                                  day=int(day)).all().delete()

    @staticmethod
    def delete_all_evaluations():
        """
        delete_all_evaluations()

        It deletes all the evaluations stored in database
        """
        Evaluation.objects.all().delete()

    def import_all_evaluations(self):
        """
        import_all_evaluations()

        It creates all objects in bulk_evaluations_to_create list at a time
        with only a commit operation
        """
        Evaluation.objects.bulk_create(self.bulk_evaluations_to_create)

    def clear_bulk_evaluations(self):
        """
        clear_bulk_evaluations()

        It clears bulk_evaluations_to_create list
        """
        self.bulk_evaluations_to_create = []

    @staticmethod
    def get_last_imported_day():
        """
        get_last_imported_day() -> value

        it returns a the last imported day
        """
        return Evaluation.objects.aggregate(Max('day')).get('day__max')

    @staticmethod
    def get_avg(player, field):
        """
        get_avg(player, field) -> value

        it returns the avg value of player field
        """
        return Evaluation.objects.filter(player=player).aggregate(
            Avg('%s' % field)).get('%s__avg' % field)

    @staticmethod
    def get_evaluated(player):
        """
        get_evaluated(player) -> int

        it returns the value of evaluated days
        """
        return Evaluation.objects.filter(player=player).filter(
            vote__gt=0).count()

    @staticmethod
    def get_fv_avg(player):
        """
        get_fv_avg(player) -> float

        it returns the fanta vote avg value of a player
        """
        evaluations = player.evaluation_set.all()
        f_votes = [e.fanta_vote for e in evaluations if e.vote > 0]
        fv_avg = float(sum(f_votes))/len(f_votes)
        return fv_avg

    @staticmethod
    def get_v_avg(player, fanta=True):
        """
        get_v_avg(player, fanta=True) -> float

        it returns the fanta vote avg value of a player if flag 'fanta'
        is True, else it returns the pure vote avg value.
        """
        evaluations = player.evaluation_set.all()
        if fanta:
            votes = [e.fanta_vote for e in evaluations if e.vote > 0]
        else:
            votes = [e.vote for e in evaluations if e.vote > 0]
        try:
            v_avg = float(sum(votes))/len(votes)
            return v_avg
        except ZeroDivisionError:
            return 0.0
