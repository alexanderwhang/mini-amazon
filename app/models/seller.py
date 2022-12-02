from flask import current_app as app


class Inventory:
    def __init__(self, user_id, product_id, name, price, quantity):
        self.product_id = product_id #from product
        self.user_id = user_id #from user
        self.name = name
        self.price = price
        self.quantity = quantity

    @staticmethod
    def get_all_inventories_by_user(user_id):
        #the colon in below area means that it is what is passed in
        rows = app.db.execute('''
SELECT Users.id, Products.id, Products.name, Products.price, Products.quantity
FROM Users, Products
WHERE Users.id = :user_id AND Users.id = Products.user_id
''',
                              user_id=user_id)
        return [Inventory(*row) for row in rows]
    
    @staticmethod
    def remove_product(user_id, product_id):
        rows = app.db.execute('''
DELETE FROM Products
WHERE user_id = :user_id AND id = :product_id
''',
                              user_id =user_id, product_id = product_id)
        return redirect(url_for('inventory.seller'))

#     @staticmethod
#     def get_all_inventories_by_product(product_id):
#         rows = app.db.execute('''
# SELECT Users.user_id, Products.product_id, Products.name, Products.price, Products.quantity
# FROM Users, Products
# WHERE Products.product_id = :product_id AND Users.user_id = Products.user_id
# ''',
#                               product_id=product_id)
#         return [Inventory(*row) for row in rows]
    
#     @staticmethod
#     def add_product(product_id, user_id, category, name, description, price, imageurl, quantity, available, avg_rating):
#         rows = app.db.execute('''
# INSERT INTO Products
# VALUES (:product_id, :user_id, :category, :name, :description, :price, :imageurl, :quantity, :available, :avg_rating)
# ''',
#                               user_id =user_id, product_id = product_id)
#         return [Inventory(*row) for row in rows]

#     @staticmethod
#     def update_product(user_id, product_id, quantity):
#         rows = app.db.execute('''
# UPDATE Products
# SET quantity = :quantity
# WHERE user_id = :user_id AND id = :product_id
# ''',
#                               user_id =user_id, product_id = product_id, quantity= quantity)
#         return [Inventory(*row) for row in rows]


class Fulfillment:
    def __init__(self, user_id, order_id, address,name, fulfillment_status, time_stamp, total_items):
        self.user_id = user_id #from orders, this is the BUYER
        self.order_id = order_id #from orders and purchases
        self.address = address #from users
        self.name = name
        self.fulfillment_status = fulfillment_status #from purchases
        self.time_stamp = time_stamp #from orders
        self.total_items = total_items #from orders 

    @staticmethod
    def get_all_fulfillment_by_user(user_id):
        rows = app.db.execute('''
SELECT Orders.user_id, Orders.id, Users.address, Products.name, Purchases.fulfillment_status, Orders.time_stamp, Orders.total_items
FROM Orders, Products, Purchases, Users
WHERE (
    Orders.id = Purchases.order_id AND
    Products.user_id = Users.id AND
    Products.id = Purchases.pid AND
    Users.id = :user_id
)
ORDER BY Orders.time_stamp DESC
''',
                              user_id=user_id)
        return [Fulfillment(*row) for row in rows]
    
    @staticmethod
    def mark_fulfilled(order_id, product_id, fulfillment_status):
        rows = app.db.execute('''
UPDATE Purchases
SET fulfillment_status = :fulfillment_status
WHERE order_id = :order_id AND product_id = :product_id
''',
                              order_id = order_id, fulfillment_status = fulfillment_status)
        return [Fulfillment(*row) for row in rows]

#     @staticmethod
#     def get_all_fulfillment_by_order(order_id):
#         rows = app.db.execute('''
# SELECT Users.user_id, Products.name, Orders.order_id, Orders.time_stamp, Orders.total_items, Users.address, Purchases.fulfillment_status
# FROM Orders, Products, Purchases, Users
# WHERE (
#     Orders.order_id = Purchases.order_id AND
#     Orders.user_id = Users.user_id AND
#     Products.product_id = Purchases.pid AND
#     Orders.order_id = :order_id
# )
# ORDER BY Orders.time_stamp DESC
# ''',
#                               order_id=order_id)
#         return [Fulfillment(*row) for row in rows]


