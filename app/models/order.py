from flask import current_app as app


class Order:
    def __init__(self, id, uid, pid, time_purchased, rating, review):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT order_id, user_id, total_price, total_items, time_stamp
FROM Orders
WHERE order_id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

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
        return [Purchase(*row) for row in rows]