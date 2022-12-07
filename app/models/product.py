from flask import current_app as app
from flask import request

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

    #get product by id
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    #get all products that are available for purchase
    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
    
    #get product by sku (same as get by id)
    @staticmethod
    def get_SKU(sku):
        rows = app.db.execute('''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
WHERE id = :sku
''',
                              sku=sku)
        return [Product(*row) for row in rows] if rows else None

    #get products that match keyword in either name or description
    @staticmethod
    def get_Name(title):
        if title is not None:
            nameSearch = f"WHERE name LIKE '%{title}%' OR description LIKE '%{title}%'"

        rows = app.db.execute(f'''
SELECT id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating
FROM Products
{nameSearch}
ORDER BY name
''',
                              title=title)
        return [Product(*row) for row in rows] if rows else None

    #get list of all categories on the site
    @staticmethod
    def get_Cat():
        rows = app.db.execute('''
SELECT *
FROM Categories
ORDER BY cat
''')
        return [Category(*row) for row in rows] if rows else None

    #get list of all products in a category
    @staticmethod
    def getbyCat(cat):
        rows = app.db.execute('''
SELECT *
FROM Products
WHERE category = :cat
''',
                                cat=cat)
        return [Product(*row) for row in rows] if rows else None
    
    #add products to the cart
    @staticmethod
    def addCart(sku, uid): #check if the product is already in the cart
        existing = app.db.execute('''
SELECT *
FROM Carts
WHERE uid = :uid AND pid = :sku
''',
                                sku=sku, uid = uid)
        if existing: #if the product is already in the cart, just update the quantity
            app.db.execute('''
UPDATE Carts
SET quantity = quantity + :qty
WHERE uid = :uid AND pid = :sku
''',
                                sku=sku, uid = uid, qty=request.form['qty'])
        else: #if product is not yet in the cart, add a new entry to the database to add it to the cart
            app.db.execute('''
INSERT INTO Carts (uid, pid, quantity, time_added_to_cart)
VALUES (:uid, :sku, :qty, DATE_TRUNC('second', CURRENT_TIMESTAMP::timestamp))
''',
                                sku=sku, uid = uid, qty=request.form['qty'])
        return

    #method to find all products sold by a user, and the number of reviews for the product. returns a list of Product objects
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
        return [Product(*row) for row in rows]

    #method for adding a product to the Products table
    @staticmethod
    def add_product(user_id, name, category, description, price, imageurl, quantity):

        #check that the quantity added is a valid integer
        try: 
            quantity = int(quantity)
        except Exception as e:
            raise BadUpdateException("Quantity must be a number")

        #check the quantity added is a positive number
        if quantity <= 0:
            raise BadUpdateException("Quantity must be greater than 0")

        #check that the price of the new product is a valid float
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
            print(str(e))
            return None

class BadUpdateException(BaseException):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg
    def toString(self):
        return self.msg