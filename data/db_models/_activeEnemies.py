import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from sqlalchemy.orm import relation
from data.gameEngine.entities.character import ActiveCharacter


class Enemy(SqlAlchemyBase, ActiveCharacter):
    __tablename__ = 'a_enemy'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    passive_id = sql.Column(sql.Integer, sql.ForeignKey('p_enemies.id'))
    passive = relation("PassiveEnemy")

    pos = sql.Column(sql.Integer)

    def __init__(self, enemy_type, pos, session):
        self.passive_id = enemy_type.id
        self.passive = enemy_type
        self.pos = pos
        session.flush()
        self.start()

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

    def dead(self, session):
        session.delete(self)
        session.commit()
