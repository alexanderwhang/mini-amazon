from flask import current_app as app

class Category:
    def __init__(self, cat):
        self.cat = cat

class Product:
    def __init__(self, product_id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating, num_reviews=None):
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
        self.num_reviews = num_reviews

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_SKU(sku):
        rows = app.db.execute('''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
WHERE id = :sku
''',
                              sku=sku)
        return [Product(*row) for row in rows] if rows else None

    @staticmethod
    def get_Name(title):
        if title is not None:
            nameSearch = f"WHERE name LIKE '%{title}%'"

        rows = app.db.execute(f'''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
{nameSearch}
ORDER BY name
''',
                              title=title)
        return [Product(*row) for row in rows] if rows else None

    @staticmethod
    def get_itemsSoldByUser(userid):
        rows = app.db.execute('''
SELECT p.id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating, count(r.id) as num_reviews
FROM Products as p
left outer join Review as r
    on p.id = r.pid
WHERE user_id = :userid
group by p.id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
''',
                              userid=userid)
        return [Product(*row) for row in rows] if rows else None

    @staticmethod
    def add_product(user_id, name, category, description, price, imageurl, quantity):
        try:
            quantity = int(quantity)
        except Exception as e:
            raise BadUpdateException("Quantity must be a number")

        if quantity <= 0:
            raise BadUpdateException("Quantity must be greater than 0")

        try:
            price = float(price)
        except Exception as e:
            raise BadUpdateException("Price must be a Float")

        try:
            rows = app.db.execute("""
INSERT INTO Products(user_id, category, name, description, price, imageurl, quantity, available, avg_rating)
VALUES(:uid, :category, :name, :description, :price, :imgurl, :quantity, True, 0)
RETURNING id
""",
                                uid=user_id, category=category, name=name, description=description, price=price,
                                imgurl=imageurl, quantity=quantity)
            id = rows[0][0]
            return Product.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

class BadUpdateException(BaseException):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg
    def toString(self):
        return self.msg