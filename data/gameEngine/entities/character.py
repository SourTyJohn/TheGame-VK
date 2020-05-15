import sqlalchemy as sql
from ast import literal_eval


BASIC_HEALTH = 20
HEALTH_PER_AGL = 2
BASIC_STAMINA = 100
STAMINA_PER_STM = 4

STATS = ['str', 'dex', 'rea', 'stm', 'agl', 'int', 'lck', 'att']
STATS_NAMES = {'str': 'Сила', 'dex': 'Ловкость', 'rea': 'Реакция', 'stm': 'Выносливость',
               'agl': 'Здоровье', 'int': 'Интеллект', 'lck': 'Удача', 'att': 'Внимательность'}

RND_NAMES = ['Абдул Альхазред', 'Чарльз Вард', 'Геральт', 'Серёга', 'Гатс', 'Джудо', 'Рихард']


class PassiveCharacter:
    name = sql.Column(sql.String, nullable=False)

    lvl = sql.Column(sql.Integer)
    exp = sql.Column(sql.Integer, default=0)

    #  Все параметры героя. Начинаются с s_
    s_free = sql.Column(sql.Integer)
    s_free_perks = sql.Column(sql.Integer)
    #  Базовые значения героя
    s_str_base = sql.Column(sql.Integer, default=0)
    s_dex_base = sql.Column(sql.Integer, default=0)
    s_rea_base = sql.Column(sql.Integer, default=0)
    s_stm_base = sql.Column(sql.Integer, default=0)
    s_agl_base = sql.Column(sql.Integer, default=0)
    s_int_base = sql.Column(sql.Integer, default=0)
    s_lck_base = sql.Column(sql.Integer, default=0)
    s_att_base = sql.Column(sql.Integer, default=0)
    #  Перки
    s_perks = sql.Column(sql.String, default='[]')

    def make_active(self):
        return ActiveCharacter()

    def all_perks(self):
        return literal_eval(self.s_perks)

    def __repr__(self):
        return f':: {self.name}. Уровень: {self.lvl}\n'


class ActiveCharacter:
    passive_id: int = 0
    passive: PassiveCharacter = None

    # Добавочные значения параметров
    s_str_add = sql.Column(sql.Integer, default=0)
    s_dex_add = sql.Column(sql.Integer, default=0)
    s_rea_add = sql.Column(sql.Integer, default=0)
    s_stm_add = sql.Column(sql.Integer, default=0)
    s_agl_add = sql.Column(sql.Integer, default=0)
    s_int_add = sql.Column(sql.Integer, default=0)
    s_lck_add = sql.Column(sql.Integer, default=0)
    s_att_add = sql.Column(sql.Integer, default=0)

    health_now = sql.Column(sql.Integer)
    health_max = sql.Column(sql.Integer)
    stamina_now = sql.Column(sql.Integer)
    stamina_max = sql.Column(sql.Integer)

    b = 0
    pos = 0

    """Вызывать в __init__  Устанавливает начальное здоровье равное максимуму"""
    def start(self):
        self.s_agl_add = 0
        self.s_stm_add = 0
        self.recalculate_params()
        self.health_now, self.stamina_now = self.health_max, self.stamina_max

    """ Пересчитывает значения максимального здоровья и выносливости. 
        Вызывать при перемене параметров"""
    def recalculate_params(self):
        self.health_max = BASIC_HEALTH + int(HEALTH_PER_AGL * (self.s_agl_add + self.passive.s_agl_base))
        self.stamina_max = BASIC_STAMINA + int(STAMINA_PER_STM * (self.s_stm_add + self.passive.s_stm_base))

    # Восстановление и урон. Последний этап
    def health_regenerate(self, amount):
        self.health_now += amount
        if self.health_now > self.health_max:
            self.health_now = self.health_max

    def stamina_regenerate(self, amount):
        self.stamina_now += amount
        if self.stamina_now > self.stamina_now:
            self.stamina_now = self.stamina_now

    def health_damage(self, amount):
        self.health_now -= amount

    def stamina_damage(self, amount):
        self.stamina_now -= amount
    # -------------------------------------

    # Получение статов add + base
    def strength(self):
        return self.s_str_add + self.passive.s_str_base

    def dexterity(self):
        return self.s_dex_add + self.passive.s_dex_base

    def reaction(self):
        return self.s_rea_add + self.passive.s_rea_base

    def stamina(self):
        return self.s_stm_add + self.passive.s_stm_base

    def agility(self):
        return self.s_agl_add + self.passive.s_agl_base

    def intelligence(self):
        return self.s_int_add + self.passive.s_int_base

    def luck(self):
        return self.s_lck_add + self.passive.s_lck_base

    def attentiveness(self):
        return self.s_att_add + self.passive.s_att_base

    def all_stats(self):
        params = {}
        tmp = [self.strength(), self.dexterity(), self.reaction(), self.stamina(),
               self.agility(), self.intelligence(), self.luck(), self.attentiveness()]
        for i, stat in enumerate(STATS):
            params[stat] = tmp[i]
        return params
    # ---------------------------

    def dodge_chance(self):
        return int(self.reaction() * 2.5 + self.luck() + self.dexterity())

    def all_perks(self):
        return self.passive.all_perks()

    def get_damage(self, source, amount, session):
        self.health_now -= amount
        s = ''
        if source == 'crit':
            s = 'КРИТ '
        if not self.is_alive():
            self.dead(session)
            return f'{s} {self.passive.name} был убит'
        return f'{s} {self.passive.name} получил {amount} урона'

    def is_alive(self):
        return self.health_now > 0

    def dead(self, session):
        pass
