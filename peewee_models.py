from peewee import *

escordia_db = SqliteDatabase('escordia_db')


class BaseModel(Model):
    class Meta:
        database = escordia_db


class PlayerModel(BaseModel):
    name = CharField(primary_key=True)
    stats = CharField()
    lvl = IntegerField()
    xp = IntegerField()
    xp_to_next_lvl = IntegerField()
    xp_rate = FloatField()
    ryo = IntegerField(default=50)
    essence = IntegerField(default=0)
    chakra = IntegerField(default=10)
    stamina = IntegerField(default=100)
    clan = CharField(default="Nenhum")
    element = CharField(default="Nenhum")
    ninja_rank = CharField(default="Estudante da Academia")
    inventory = CharField()
    equipment = CharField()
    skills = CharField()
    passives = CharField()
    current_area = IntegerField(default=1)
    in_fight = BooleanField(default=False)
    in_dungeon = BooleanField(default=False)
    defeated_bosses = CharField(default="[]")
    blessings = CharField(default="[]")
    missions_completed = CharField(default="{}")
    active_mission = CharField(default="None")
    mission_end_time = FloatField(default=0)
