from peewee import *

db = SqliteDatabase('db.sqlite')


class BaseModel(Model):
    class Meta:
        database = db


class Company(BaseModel):
    name = TextField()
    password = TextField()


class Product(BaseModel):
    name = TextField()
    price = FloatField()
    category = TextField()

    # кожен товар належить певній компанії
    # products - список товарів, який належить компанії
    company = ForeignKeyField(Company, backref='products')


def init_db():
    db.connect()
    # db.drop_tables([Product, Company])
    db.create_tables([Product, Company])