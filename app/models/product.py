from flask import current_app as app


class Product:
    def __init__(self, product_id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating):
        self.product_id = product_id
        self.user_id = user_id
        self.category = category
        self.name = name
        self.description = description
        self.price = price
        self.imageurl = imageurl
        self.quantity = quantity
        self.available = available
        self.avg_rating = avg_rating

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE product_id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
