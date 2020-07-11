import emoji


class Product:

    CSV_FIELD_NAMES = [
        'id',
        'name',
        'description',
        'category',
        'sub_category',
        'price',
        'old_price',
        'unit_type',
        'isNew',
        'isForSale',
        'image'
    ]

    def __init__(self, prodId):
        self.id = prodId
        self.name = ''
        self.description = ''
        self.category = ''
        self.sub_category = ''
        self.price = 0
        self.old_price = 0
        self.unit_type = 'יח׳'
        self.isNew = False
        self.isForSale = False
        self.image = ''

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

    def print_terminal(self):
        if float(self.old_price) < float(self.price):
            sign = ':red_triangle_pointed_up:'
        else:
            sign = ':down_arrow:'
        print(emoji.emojize("{}, לפני:{} אחרי:{}, {}".format(
            self.name,
            self.old_price,
            self.price,
            sign
        )))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'sub_category': self.sub_category,
            'price': self.price,
            'old_price': self.old_price,
            'unit_type': self.unit_type,
            'isNew': self.isNew,
            'isForSale': self.isForSale,
            'image': self.image
        }
