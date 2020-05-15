import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
from ast import literal_eval

from data.db_models._marketLot import LotSell, LotBuy, COMMISSION, COMMISSION_TEXT
from data.db_models._activeHeroes import ActiveHero

from core import server
from sqlalchemy.orm import relation


MAX_HEROES = 6


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    vk_id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    """Активные герои игрока"""
    hero1 = sql.Column(sql.Integer, sql.ForeignKey('a_heroes.id'), nullable=True)
    hero2 = sql.Column(sql.Integer, sql.ForeignKey('a_heroes.id'), nullable=True)
    hero3 = sql.Column(sql.Integer, sql.ForeignKey('a_heroes.id'), nullable=True)

    h1 = relation("ActiveHero", foreign_keys=[hero1])
    h2 = relation("ActiveHero", foreign_keys=[hero2])
    h3 = relation("ActiveHero", foreign_keys=[hero3])

    idle_hero1 = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)
    idle_hero2 = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)
    idle_hero3 = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)
    idle_hero4 = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)
    idle_hero5 = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)
    idle_hero6 = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)

    ih1 = relation("PassiveHero", foreign_keys=[idle_hero1])
    ih2 = relation("PassiveHero", foreign_keys=[idle_hero2])
    ih3 = relation("PassiveHero", foreign_keys=[idle_hero3])
    ih4 = relation("PassiveHero", foreign_keys=[idle_hero4])
    ih5 = relation("PassiveHero", foreign_keys=[idle_hero5])
    ih6 = relation("PassiveHero", foreign_keys=[idle_hero6])

    good_inventory = sql.Column(sql.String, default='{}')  # dict {"item_id": count}
    money = sql.Column(sql.Integer, default=1000)

    """Сражение в котором участвует игрок"""
    battle = sql.Column(sql.Integer, sql.ForeignKey('battles.id'), nullable=True)
    b = relation("Battle", foreign_keys=[battle], post_update=True)

    keyboard = sql.Column(sql.SmallInteger, default=1)
    page = sql.Column(sql.Integer, default=0)
    search = sql.Column(sql.String, nullable=True)

    selected_slot = sql.Column(sql.Integer, nullable=True)
    selected_slot_2 = sql.Column(sql.Integer, nullable=True)

    battle_won = sql.Column(sql.Integer, default=0)

    def __init__(self, vk_id):
        self.vk_id = vk_id
        self.keyboard = 2

    def heroes_exit(self, session):
        if self.h1:
            self.h1.exit(session, self)
        if self.h2:
            self.h2.exit(session, self)
        if self.h3:
            self.h3.exit(session, self)

    def new_hero(self, session, hero_id):
        idle_heroes = self.get_heroes_list()
        i = len(idle_heroes)
        if i < MAX_HEROES:
            if i == 0:
                self.idle_hero1 = hero_id
            elif i == 1:
                self.idle_hero2 = hero_id
            elif i == 2:
                self.idle_hero3 = hero_id
            elif i == 3:
                self.idle_hero4 = hero_id
            elif i == 4:
                self.idle_hero5 = hero_id
            elif i == 5:
                self.idle_hero6 = hero_id
            session.commit()
            return True
        return False

    def del_hero(self, session, hero, k):
        pass

    def activate_hero(self, hero, slot, session):
        active = hero.active(session, slot)

        '''Если такой герой уже создан, то существующий удалиться'''
        exists = session.query(ActiveHero).filter(active.passive_id == ActiveHero.passive_id).first()
        if exists:
            exists.exit(session, self)

        session.add(active)
        session.commit()

        if slot == 1:
            self.hero1 = active.id
        elif slot == 2:
            self.hero2 = active.id
        elif slot == 3:
            self.hero3 = active.id

        session.commit()

    def get_heroes_list(self) -> list:
        return [x for x in [self.ih1, self.ih2, self.ih3, self.ih4, self.ih5, self.ih6] if x]

    def good_inventory_dict(self) -> dict:
        return literal_eval(self.good_inventory)

    def set_keyboard(self, k_index, session):
        self.keyboard = k_index
        session.flush()

    # gameEngine type
    def get_item(self, item_id, session, count=1):
        inventory = self.good_inventory_dict()

        if item_id in inventory.keys():
            inventory[item_id] += count
        else:
            inventory[item_id] = count

        self.good_inventory = str(inventory)
        session.flush()

    def remove_item(self, item_id, session, count=1):
        inventory = self.good_inventory_dict()

        if item_id in inventory.keys() and inventory[item_id] >= count:
            if inventory[item_id] == count:
                inventory[item_id] = 0
                del inventory[item_id]
            else:
                inventory[item_id] -= count

            self.good_inventory = str(inventory)
            session.flush()
            return True

        return False

    def get_money(self, amount, session):
        self.money += int(amount)
        session.flush()

    def spend_money(self, amount, session):
        amount = int(amount)

        if self.money >= amount:
            self.money -= amount
            session.flush()
            return True
        else:
            return False
    #

    # marketplace
    def sell(self, item, price, session):
        price_with_com = int(price + price * COMMISSION)
        lots = session.query(LotBuy).filter((LotBuy.item_id == item), (LotBuy.price == price_with_com)).all()

        if not self.remove_item(item, session):
            return 'У вас нет этого предмета'

        if lots:
            for lot in lots:
                if item_transfer(self, lot.owner, item, price, session):
                    session.delete(lot)
                    session.flush()
                    server.notification(lot.owner.vk_id, f'Куплен предмет {item} за {price}')
                    return f'Предмет продан. +{price} = {self.money} золота'

        session.add(LotSell(item, self.vk_id, price_with_com))
        session.flush()
        return f'Предмет выставлен на тогровую площадку за {price_with_com} (комиссия {COMMISSION_TEXT})'

    def buy(self, item, price, session, count=1):
        k = 0

        lots = session.query(LotSell).filter((LotSell.item_id == item), (LotSell.price == price)).all()
        if lots:
            for lot in lots:
                if item_transfer(lot.owner, self, item, price, session):
                    session.delete(lot)
                    session.flush()
                    server.notification(lot.owner.vk_id, f'У Вас купили {item} за {price - price * COMMISSION}')
                    k += 1
                if k == count:
                    break

        if k:
            msg = f'Предметы ({k}шт.) куплены. - {price}*{k} = {self.money} золота\n'
        else:
            msg = ''
        if count != k:
            msg += f'Ваши запросы на покупку {item} ({count - k}шт.) выставлены на тогровую площадку'
            session.add_all([LotBuy(item, self.vk_id, price) for _ in range(count - k)])
            session.flush()

        return msg
    #


def item_transfer(sell: User, buy: User, item, price, session):
    if buy.spend_money(price, session):
        sell.get_money(price - price * COMMISSION, session)
        buy.get_item(item, session)
        return True
    return False
