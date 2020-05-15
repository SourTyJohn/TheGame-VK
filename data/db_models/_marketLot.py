import sqlalchemy as sql
from sqlalchemy.orm import relation

from data.db_session import SqlAlchemyBase
from data.db_models._items import id_to_class


COMMISSION = 0.1
COMMISSION_TEXT = f'{COMMISSION * 100}%'


class Lot:
    id = 0
    '''Лот или запрос на покупку на торговой площадке'''

    def __init__(self, item_id, user_id, price):
        self.item_id = item_id
        self.owner_id = user_id
        self.price = price

    def __repr__(self):
        item = id_to_class(self.item_id)
        return f'{self.id} ({self.item_id}) {item.name}, Цена: {self.price}, Редкость: {item.rarity}\n'


class LotSell(Lot, SqlAlchemyBase):
    __tablename__ = 'lot_sell'

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    price = sql.Column(sql.Integer, nullable=False)

    owner_id = sql.Column(sql.Integer, sql.ForeignKey('users.vk_id'))
    owner = relation('User')

    item_id = sql.Column(sql.String, sql.ForeignKey('items.id'))
    item = relation('Item')

    def __repr__(self):
        return super().__repr__()


class LotBuy(Lot, SqlAlchemyBase):
    __tablename__ = 'lot_buy'

    id = sql.Column(sql.Integer, primary_key=True, autoincrement=True)
    price = sql.Column(sql.Integer, nullable=False)

    owner_id = sql.Column(sql.Integer, sql.ForeignKey('users.vk_id'))
    owner = relation('User')

    item_id = sql.Column(sql.String, sql.ForeignKey('items.id'))
    item = relation('Item')
