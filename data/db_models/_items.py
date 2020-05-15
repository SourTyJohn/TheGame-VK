import sqlalchemy as sql
from data.db_session import SqlAlchemyBase

from data.gameEngine.contents.items import *
from random import random

ID_PREFIX = [None, 'i_', 'w_', 't_']
ITEM_TYPES = [None, 'Предмет', 'Материал', 'Расходник', 'Диковинка', 'Оружие', 'Тринкет']

"""level: [%, % per LUCK of hero]"""
DROP_CHANCE = {
    1: [50, -2],
    2: [30, -0.1],
    3: [10, 0.8],
    4: [6, 0.7],
    5: [3.4, 0.6],
    6: [0.6, 0.3],
    7: [-200, 0.2]
}


"""Все классы предметов из модулей contents. Заполняется с запуском main.py"""
ITEMS = {}

"""LootTable - таблицы лута от разных источников"""
LT_DUNGEON = LootTable()
LT_BOX = LootTable()
LT_WEAPON_BOX = LootTable()


class Item(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sql.Column(sql.String, primary_key=True)
    item_type = sql.Column(sql.Integer, nullable=False)  # 1 - item, 2 - weapon, 3 - trinket

    name = sql.Column(sql.String, default='?ItemName?')
    rarity = sql.Column(sql.Integer, default=0)

    def __init__(self, item_class, loot_tables=None):
        self.name, self.rarity, self.item_type, self.id = item_class.set()

        ITEMS[self.id] = item_class
        for x in loot_tables:
            x.add_loot(item_class)


def init_items(session):
    session.query(Item).delete()
    session.add_all([
        Item(w_Fist, []),

        Item(i_Bread, [LT_DUNGEON, LT_BOX]),
        Item(i_HolyWater, [LT_DUNGEON, LT_BOX]),
        Item(i_Clover, [LT_DUNGEON, LT_BOX]),
        Item(i_WaterBottle, [LT_DUNGEON, LT_BOX]),
        Item(i_SmallMoney, [LT_DUNGEON, LT_BOX]),
        Item(i_LuckyBox, [LT_DUNGEON]),

        Item(w_Dagger, [LT_DUNGEON, LT_BOX]),
        Item(w_GreatSword, [LT_DUNGEON, LT_BOX]),
        Item(w_Crossbow, [LT_DUNGEON, LT_BOX]),
        Item(w_RustySword, [LT_DUNGEON]),

        # Item(t_BaseTrinket, [LT_DUNGEON, LT_BOX])
    ])
    session.commit()

    print('all items inited')


def show_item(item_id, full=False):
    item = id_to_class(item_id)

    if full:
        description = f'{item.name} - {ITEM_TYPES[item.item_type]}'
        for string in item.description:
            description += f'\n{string}\n'

    else:
        description = f'({item_id}) {item.name}'

    return description


def show_inventory(inventory: dict, inv_filter=None):
    result = ''
    for i, x in enumerate(inventory.keys()):
        if inv_filter is not None:
            pass

        result += f'{i + 1}. {show_item(x, False)}: {inventory[x]}шт.\n'
    return result, len(inventory.keys())


def id_to_class(item_id):
    return ITEMS[item_id]


def getRngItemInDungeon(user, session):
    luck = max([x for x in [user.h1, user.h2, user.h3] if x], key=lambda x: x.luck()).luck()
    return getRngItem(user, session, LT_DUNGEON, luck)


def lootRarity(luck):
    rnd, lvl = random() * 100, 1
    for x in range(len(DROP_CHANCE), 0, -1):
        if rnd <= DROP_CHANCE[x][0] + DROP_CHANCE[x][1] * luck:
            lvl = x
            break
    return lvl


def getRngItem(user, session, loot_table, luck=0):
    msg = ''

    while True:
        item_rarity = lootRarity(luck)
        possible_items = loot_table[item_rarity]
        item = ITEMS[possible_items[ri(0, len(possible_items) - 1)]]

        user.get_item(item.id, session)
        msg += f'Получен предмет: ({item.id}) {item.name}. Редкость:{item_rarity}\n'

        if DROP_CHANCE[item_rarity][0] <= random() * 100:
            break

    return msg
