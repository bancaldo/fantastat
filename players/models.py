# noinspection PyUnresolvedReferences
from django.db import models


class Player(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=50)
    real_team = models.CharField(max_length=3)
    role = models.CharField(max_length=25)
    cost = models.IntegerField()
    objects = models.Manager()  # pycharm inspection workaround

    def __unicode__(self):
        return self.name


class Evaluation(models.Model):
    day = models.IntegerField()
    vote = models.FloatField()
    fanta_vote = models.FloatField()
    cost = models.IntegerField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    objects = models.Manager()  # pycharm inspection workaround

    # noinspection PyUnresolvedReferences
    def __unicode__(self):
        return '[%s][%s]' % (self.day, self.player.code)
