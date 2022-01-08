from marshmallow import Schema, fields


class ProductData:
    def __init__(self, name):
        self.name = name


class PriceData:
    def __init__(self, currency, unit_amount, product_data):
        self.currency = currency
        self.unit_amount = unit_amount
        self.product_data = product_data


class LineItems:
    def __init__(self, price_data, quantity):
        self.price_data = price_data
        self.quantity = quantity 


class Metadata:
    def __init__(self, user_profile_id):
        self.user_profile_id = user_profile_id
        

class ProductDataSchema(Schema):
    name = fields.Str()


class PriceDataSchema(Schema):
    currency = fields.Str()
    unit_amount = fields.Int()
    product_data = fields.Nested(ProductDataSchema)


class LineItemsSchema(Schema):
    price_data = fields.Nested(PriceDataSchema)
    quantity = fields.Int()


class MetadataSchema(Schema):    
    user_profile_id = fields.Int()