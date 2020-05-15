from data.gameEngine.contents.attacks import *
from data.db_models._items import ITEMS
from random import randint as ri


class EnemyType:
    id = 0
    name = '?EnemyName?'
    lvl = 0

    s_rea_base = 0
    s_stm_base = 0
    s_agl_base = 0
    s_int_base = 0
    s_att_base = 0
    s_str_base = 0
    s_dex_base = 0
    s_lck_base = 0

    weapon = ''

    @classmethod
    def make_turn(cls, user, session):
        pass


class e_SkeletonWeak(EnemyType):
    id = 1
    name = 'Древний скелет'
    lvl = 7

    s_str_base = 4
    s_dex_base = 1
    s_lck_base = 2
    s_agl_base = -3

    weapon = 'w_rus'

    slash = SpookySlash
    throw = BoneThrow

    @classmethod
    def make_turn(cls, user,  session, **kwargs):
        teams = [[user.b.e1, user.b.e2, user.b.e3], [user.h1, user.h2, user.h3]]
        actor = kwargs['actor']

        if actor.pos in [1, 2]:
            if user.h1 and not user.h2:
                result = cls.slash.do(actor, ITEMS[cls.weapon], *teams, 0, session)
            elif user.h2 and not user.h1:
                result = cls.slash.do(actor, ITEMS[cls.weapon], *teams, 1, session)
            elif user.h1 and user.h2:
                result = cls.slash.do(actor, ITEMS[cls.weapon], *teams, ri(0, 1), session)
            else:
                result = 'Пропуск хода'
        else:
            result = cls.throw.do(actor, ITEMS[cls.weapon], *teams, ri(0, 2), session)
        return result


# -------------~
# ENEMY GROUP
# -------------~


ENEMY_GROUPS = {}


class ge_EnemyGroup:
    level = 0
    enemies = []


class ge_FirstEncounter(ge_EnemyGroup):
    level = 7
    enemies = [1, None, None]


class ge_WeakSkeletons(ge_EnemyGroup):
    level = 7
    enemies = [1, 1, 1]


ENEMY_GROUPS[1] = ge_FirstEncounter
ENEMY_GROUPS['WeakS'] = ge_WeakSkeletons
