from bidi.algorithm import get_display

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

    def print_terminal(self):
        print("id: {}, name: '{}', sub_cat: '{}', price: {}, old_price: {}, units: {}, isNew: {}".format(
            self.id,
            get_display(self.name),
            get_display(self.sub_category),
            self.price,
            self.old_price,
            get_display(self.unit_type),
            self.isNew
        ))

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

