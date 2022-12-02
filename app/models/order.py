from flask import current_app as app


class Order:
    def __init__(self, order_id, uid, total_price, total_items, time_stamp):
        self.order_id = order_id
        self.uid = uid
        self.total_price = total_price
        self.total_items = total_items
        self.time_stamp = time_stamp


    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, user_id, total_price, total_items, time_stamp
FROM Orders
WHERE id = :id
''',
                              id=id)
        return Order(*(rows[0])) if rows else None
        
    @staticmethod
    def get_all_orders_by_user(user_id):
        rows = app.db.execute('''
SELECT id, user_id, total_price, total_items, time_stamp
FROM Orders
WHERE user_id = :user_id
''',
                              user_id=user_id)
        return Order(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT order_id, user_id, total_price, total_items, time_stamp
FROM Purchases
WHERE user_id = :uid
AND time_stamp >= :since
ORDER BY time_stamp DESC
''',
                              uid=uid,
                              since=since)
        return [Order(*row) for row in rows]