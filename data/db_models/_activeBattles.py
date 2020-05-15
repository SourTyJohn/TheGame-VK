import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from sqlalchemy.orm import relation
from data.gameEngine.contents.enemies import *
from data.db_models._passiveEnemies import ENEMIES
from data.db_models._activeHeroes import ActiveHero
from data.db_models._activeEnemies import Enemy
from math import trunc
from ast import literal_eval


class Battle(SqlAlchemyBase):
    __tablename__ = 'battles'

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    player = sql.Column(sql.Integer, sql.ForeignKey("users.vk_id"))
    p = relation("User", foreign_keys=[player])

    enemy_1 = sql.Column(sql.Integer, sql.ForeignKey("a_enemy.id"))
    enemy_2 = sql.Column(sql.Integer, sql.ForeignKey("a_enemy.id"))
    enemy_3 = sql.Column(sql.Integer, sql.ForeignKey("a_enemy.id"))

    e1 = relation("Enemy", foreign_keys=[enemy_1])
    e2 = relation("Enemy", foreign_keys=[enemy_2])
    e3 = relation("Enemy", foreign_keys=[enemy_3])

    lvl = sql.Column(sql.Integer)  # Уровень боя
    turn_now = sql.Column(sql.Integer, default=0)  # Текущий ход
    turns = sql.Column(sql.String)  # Порядок ходов
    # 1, 2, 3, 4, 5, 6

    def __init__(self, player, session):
        self.player = player.vk_id
        group = None

        if player.battle_won == 0:
            group = ENEMY_GROUPS[1]

        else:
            group = ENEMY_GROUPS['WeakS']
            group_lvl = group_level(player)
            pass

        self.init_from_group(session, player, group)

    def init_from_group(self, session, player, enemy_group):
        inited = init_group(enemy_group, session)
        entities = []

        if inited[1]:
            self.enemy_1 = inited[1].id
            entities.append(inited[1])
        if inited[2]:
            self.enemy_2 = inited[2].id
            entities.append(inited[2])
        if inited[3]:
            self.enemy_3 = inited[3].id
            entities.append(inited[3])

        if player.h1:
            entities.append(player.h1)
        if player.h2:
            entities.append(player.h2)
        if player.h3:
            entities.append(player.h3)

        self.lvl = enemy_group.level
        self.turns = str([x.__class__.__name__[0] + str(x.id) for x in sorted(entities, key=lambda x: -x.reaction())])
        session.commit()

    def close(self, session):
        if self.e1:
            session.delete(self.e1)
        if self.e2:
            session.delete(self.e2)
        if self.e3:
            session.delete(self.e3)
        self.p.b = None  # Убирает статус боя у игрока
        session.delete(self)
        session.commit()

    def play(self, session):
        condition = self.check_condition()
        if condition == '#CONTINUE':

            turn = literal_eval(self.turns)[self.turn_now]
            if turn[0] == 'A':
                result = self.user_turn(turn, session)
            else:
                result = self.enemy_turn(turn, session)

            if result:
                return result

            self.next_turn()
            return self.play(session)

        else:
            return condition

    def user_turn(self, turn, session):
        self.p.set_keyboard(21, session)
        self.p.selected_slot_2 = turn[1:]
        h = session.query(ActiveHero).get(turn[1:])

        if h:
            return f'Ваш ход! {h.passive.name} действует\n{self.show()}\n\n'
        return False

    def enemy_turn(self, turn, session):
        enemy = session.query(Enemy).get(int(turn[1:]))

        if enemy:
            result = ENEMIES[enemy.passive.id][1].make_turn(self.p, session, actor=enemy)
            self.next_turn()
            self.p.set_keyboard(24, session)
            return result
        return False

    def next_turn(self):
        max_turn = len(literal_eval(self.turns)) - 1
        if self.turn_now == max_turn:
            self.turn_now = 0
        else:
            self.turn_now += 1

    def show(self):
        des = 'Ваша группа\n'
        for x in [self.p.h3, self.p.h2, self.p.h1]:
            if x:
                des += f'{x.pos} {x.passive.name}\n Зд. {x.health_now} /' \
                       f' {x.health_max} // Вн. {x.stamina_now} / {x.stamina_max}\n==========\n'

        des += '\n\nВраг\n'
        for x in [self.e1, self.e2, self.e3]:
            if x:
                des += f'{x.pos} {x.passive.name}\n Зд. {x.health_now} /' \
                       f' {x.health_max} // Вн. {x.stamina_now} / {x.stamina_max}\n==========\n'
        return des

    def check_condition(self):
        if not any([self.e1, self.e2, self.e3]):
            return '#P_WIN'
        if not (any([self.p.h1, self.p.h2, self.p.h3])):
            return '#P_LOSE'
        return '#CONTINUE'


def group_level(player):
    group = [x.passive.lvl for x in [player.h1, player.h2, player.h3] if x]
    level = trunc(sum(group) / len(group))
    return level


def init_group(group, session):
    ids = {1: None, 2: None, 3: None}
    for i, id in enumerate(group.enemies):
        if id:
            act = ENEMIES[id][0].active(i + 1, session)
            session.add(act)
            session.flush()
            ids[i + 1] = act

    session.commit()
    return ids
