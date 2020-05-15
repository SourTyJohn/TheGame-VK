import sqlalchemy as sql
from data.db_session import SqlAlchemyBase
import sqlalchemy.orm as orm
from data.gameEngine.entities.character import ActiveCharacter
from sqlalchemy.orm import relation
from data.gameEngine.contents.attacks import ATTACKS
from data.db_models._items import ITEMS


#  Эта таблица хранит все параметры героев, которые в данный момент на вылазке
class ActiveHero(SqlAlchemyBase, ActiveCharacter):
    __tablename__ = 'a_heroes'
    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)

    passive_id = sql.Column(sql.Integer, sql.ForeignKey('p_heroes.id'), nullable=True)
    passive = orm.relation('PassiveHero')

    weapon = sql.Column(sql.String, sql.ForeignKey("items.id"))
    w = relation("Item", foreign_keys=[weapon])

    trinket = sql.Column(sql.String, sql.ForeignKey("items.id"))
    t = relation("Item", foreign_keys=[trinket])

    pos = sql.Column(sql.Integer, nullable=False)

    def __init__(self, p_hero, session, pos):
        self.passive_id = p_hero.id
        self.passive = p_hero
        self.pos = pos
        session.commit()
        self.start()

    def __repr__(self):
        res = f':: {self.passive.name}. Уровень: {self.passive.lvl}\n'
        if self.weapon:
            res += f'Оружие: {self.w.name}'
        return res

    def exit(self, session, user):
        if self.trinket:
            user.get_item(self.trinket, session)

        if self.weapon:
            user.get_item(self.weapon, session)

        session.delete(self)

        if self.pos == 1:
            self.passive.owner.h1 = None
        elif self.pos == 2:
            self.passive.owner.h2 = None
        else:
            self.passive.owner.h3 = None

        session.flush()

    def give_weapon(self, user, weapon_id, session):
        if not user.remove_item(weapon_id, session):
            return 'У Вас нет этого предмета'

        if self.weapon is not None:
            user.get_item(self.weapon, session)

        self.weapon = weapon_id
        session.flush()
        return 'Оружие экипировано'

    def give_trinket(self, user, trinket_id, session):
        if not user.remove_item(trinket_id, session):
            return 'У Вас нет этого предмета'

        if self.trinket is not None:
            user.get_item(self.trinket, session)
        self.trinket = trinket_id
        session.flush()
        return 'Амулет экипирован'

    def get_attacks(self):
        if self.weapon:
            return ITEMS[self.weapon].attacks, len(ITEMS[self.weapon].attacks)
        else:
            return ITEMS['Fist'].attacks, len(ITEMS['Fist'].attacks)

    def dead(self, session):
        session.delete(self)
        if self.weapon:
            self.passive.owner.get_item(self.weapon, session)
        session.commit()
