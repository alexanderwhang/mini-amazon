from flask import current_app as app

# the Orders class has all the componenets to load the orders for a user on our ecommerce site
class Orders:
    def __init__(self, oid, uid, tot_price, tot_items, time):
        self.oid = oid
        self.uid = uid
        self.tot_price = tot_price
        self.tot_items = tot_items
        self.time = time

    # this method gets all of the orders from a specific user
    @staticmethod
    def get_all_orders_by_user(user_id):
        rows = app.db.execute('''
SELECT id, user_id, total_price, total_items, time_stamp
FROM Orders
WHERE user_id = :user_id
''',
                              user_id=user_id)
        return [Orders(*row) for row in rows]

    @staticmethod
    def getOrderPrice(order_id):
        rows = app.db.execute('''
SELECT total_price
FROM Orders
WHERE id = :id
''',
                              id=order_id)
        return rows[0][0]
