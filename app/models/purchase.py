from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, time_purchased, rating, review):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.rating = rating
        self.review = review

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_reviews(id=0):
        rows = app.db.execute('''
        SELECT id, uid, pid, time_purchased, rating, review
        FROM Purchases
        ''',
        id=id
        )
        return [Purchase(*row) for row in rows]
