import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from ._activeEnemies import Enemy
from data.gameEngine.contents.enemies import *
from data.gameEngine.entities.character import PassiveCharacter



ENEMIES = {}


#  Эта таблица хранит все параметры героев, которые в данный момент не на вылазке
class PassiveEnemy(SqlAlchemyBase, PassiveCharacter):
    __tablename__ = 'p_enemies'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    def __init__(self, enemy_class):
        self.id = enemy_class.id
        self.name = enemy_class.name
        self.lvl = enemy_class.lvl

        self.s_str_base = enemy_class.s_str_base
        self.s_dex_base = enemy_class.s_dex_base
        self.s_rea_base = enemy_class.s_rea_base
        self.s_stm_base = enemy_class.s_stm_base
        self.s_lck_base = enemy_class.s_lck_base
        self.s_int_base = enemy_class.s_int_base
        self.s_agl_base = enemy_class.s_agl_base
        self.s_att_base = enemy_class.s_att_base

        ENEMIES[self.id] = [self, enemy_class]

    def __repr__(self):
        return f':: {self.name}. Уровень: {self.lvl}\n'

    def open_stats(self):
        return {'str': self.s_str_base, 'dex': self.s_dex_base, 'rea': self.s_rea_base,
                'stm': self.s_stm_base, 'agl': self.s_agl_base, 'int': self.s_int_base,
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

    def active(self, pos, session):
        return Enemy(self, pos, session)


def init_enemies(session):
    session.query(PassiveEnemy).delete()

    session.add_all([
        PassiveEnemy(e_SkeletonWeak),
    ])

    session.commit()
    session.close()

    print('all enemies inited')
