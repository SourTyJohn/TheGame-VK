import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from ._activeHeroes import ActiveHero
from data.gameEngine.entities.character import PassiveCharacter, STATS, STATS_NAMES
from sqlalchemy.orm import relation


#  Эта таблица хранит все параметры героев, которые в данный момент не на вылазке
class PassiveHero(SqlAlchemyBase, PassiveCharacter):
    __tablename__ = 'p_heroes'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    owner_id = sql.Column(sql.Integer, sql.ForeignKey('users.vk_id'))
    owner = relation('User', foreign_keys=[owner_id])

    def __init__(self, name, owner_id, level=9):
        self.name = name
        self.lvl = level
        self.s_free = level
        self.s_free_perks = level // 10
        self.owner_id = owner_id

    def __repr__(self):
        return f':: {self.name}. Уровень: {self.lvl}\n'

    def open_stats(self):
        return {'str': self.s_str_base, 'dex': self.s_dex_base, 'rea': self.s_rea_base,
                'stm':self.s_stm_base, 'agl': self.s_agl_base, 'int': self.s_int_base,
                'lck': self.s_lck_base, 'att': self.s_att_base, 'free': self.s_free}

    def close_stats(self, stats):
        self.s_str_base = stats['str']
        self.s_dex_base = stats['dex']
        self.s_rea_base = stats['rea']
        self.s_stm_base = stats['stm']
        self.s_agl_base = stats['agl']
        self.s_int_base = stats['int']
        self.s_lck_base = stats['lck']
        self.s_att_base = stats['att']
        self.s_free = stats['free']

    def active(self, session, pos):
        return ActiveHero(self, session, pos)

    def show(self):
        description = str(self)
        description += f'Опыта {self.exp} / {self.exp_to_level_up()}\n'
        description += f'str Сила__________ {self.s_str_base}\n' \
                       f'dex Ловкость______ {self.s_dex_base}\n' \
                       f'rea Реакция_______ {self.s_rea_base}\n' \
                       f'stm Выносливость__ {self.s_stm_base}\n' \
                       f'agl Телосложение__ {self.s_agl_base}\n' \
                       f'int Интеллект_____ {self.s_int_base}\n' \
                       f'lck Удача_________ {self.s_lck_base}\n' \
                       f'att Внимательность {self.s_att_base}\n' \
                       f'Очки параметров___ {self.s_free}'

        return description

    def get_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_level_up():
            self.lvl += 1
            return f'{self.name} получил {amount} опыта. Достигнут {self.lvl} уровень!'
        return f'{self.name} получил {amount} опыта.'

    def exp_to_level_up(self):
        return int((self.lvl - 8) ** 2 * 500)
