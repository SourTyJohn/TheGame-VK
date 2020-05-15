from data.gameEngine.entities.character import ActiveCharacter
from random import randint as ri


class Attack:
    name = '?AttackName?'
    desc = ""
    self_pos = []  # Список позиций с которых можно использовать эту атаку
    target_pos = []  # Список позиций по которым можно бить этой атакой
    damage_multiply = 1  # Множитель урона
    accuracy = 100  # Шанс попадания в процентах. Может быть больше 100
    stamina_consume = 0  # Затраты выносливости на использование
    crit_multiply = 1

    @classmethod
    def may_choose(cls, actor_pos):
        return actor_pos in cls.self_pos

    @classmethod
    def may_do(cls, target_pos):
        return target_pos in cls.target_pos

    @classmethod
    def hit_chance(cls, actor: ActiveCharacter, target: ActiveCharacter):
        return cls.accuracy + actor.s_lck_add - target.dodge_chance()

    @classmethod
    def description(cls, hero, weapon):
        damage, crit = cls.trueAttDamage(hero, weapon)

        des = f' _ <{cls.name}> \n' \
              f'| Урон: {damage[0]} - {damage[1]}\n' \
              f'| Меткость: {cls.accuracy}%\n' \
              f'| Выносливости: {cls.stamina_consume}\n' \
              f'| Шанс крит.урона: {crit * cls.crit_multiply}\n' \
              f'| Целевые позиции {cls.target_pos}\n' \
              f'| Можно атаковать с {cls.self_pos}\n' \
              f'| Персонаж сейчас на позиции: {hero.pos}'
        return des

    @classmethod
    def trueAttDamage(cls, hero, weapon):
        damage, crit = weapon.trueDamage(hero, cls.damage_multiply)
        return damage, crit * cls.crit_multiply

    @classmethod
    def do(cls, actor, weapon, allies: list, enemies: list, target_pos, session):
        if not enemies[target_pos]:
            return False

        damage = cls.trueAttDamage(actor, weapon)
        res = f'{actor.passive.name} использует навык {cls.name}\n'

        if ri(0, 100) < damage[1]:
            return res + enemies[target_pos].get_damage('crit', damage[0][1] * 2, session)
        return res + enemies[target_pos].get_damage(None, ri(damage[0][0], damage[0][1]), session)


#  SKELETONS

class BoneThrow(Attack):
    name = 'Бросок кости'
    self_pos = [3, ]
    target_pos = [1, 2, 3]
    damage_multiply = 0.4
    accuracy = 80
    stamina_consume = 5


class SpookySlash(Attack):
    name = 'Жуткий порез'
    self_pos = [1, 2]
    target_pos = [1, 2]
    damage_multiply = 0.7
    accuracy = 95
    stamina_consume = 5


#


#


class Punch(Attack):
    name = 'Удар кулаком'
    self_pos = [1, ]
    target_pos = [1, ]
    damage_multiply = 1
    accuracy = 100
    stamina_consume = 10


class DirtyStab(Attack):
    name = 'Подлый тычёк'
    self_pos = [1, ]
    target_pos = [1, 2]
    damage_multiply = 1
    accuracy = 100
    stamina_consume = 20


#  SWORDS
class CockyThrust(Attack):
    name = 'Дерзкий выпад'
    self_pos = [1, 2]
    target_pos = [1, 2, 3]
    damage_multiply = 0.6
    accuracy = 70
    crit_multiply = 2
    stamina_consume = 32


class BraveSlash(Attack):
    name = 'Меткий удар'
    self_pos = [1, ]
    target_pos = [1, ]
    damage_multiply = 1
    accuracy = 100
    crit_multiply = 1
    stamina_consume = 32


#  BOMBS
class BombThrow(Attack):
    name = 'Бросок бомбы'
    desc = ''
    self_pos = [2, 3]
    target_pos = [2, 3]
    damage_multiply = 1
    accuracy = 70
    crit_multiply = 1
    stamina_consume = 10


class N:
    pass


ATTACKS = {
    'DiS': DirtyStab,
    'CoT': CockyThrust,
    'BrS': BraveSlash,
    'Punch': Punch,
}
