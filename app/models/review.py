from flask import current_app as app


class Review:
    """
    This is just a TEMPLATE for Review, you should change this by adding or 
        replacing new columns, etc. for your design.
    """
    def __init__(self, id, uid, pid, review_time, review_content, review_rating):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.review_time = review_time
        self.review_content = review_content
        self.review_rating = review_rating

    @staticmethod
    def user_email_to_id(user_email):
        rows = app.db.execute (
            """
            SELECT id
            FROM Users
            WHERE email = :user_email
            """,
            user_email=user_email
        )
        return rows[0][0]

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute (
            '''
            SELECT *
            FROM Review
            WHERE uid = :uid
            ORDER BY review_time DESC
            ''',
            uid=uid
        )
        return [Review(*row) for row in rows]

    @staticmethod
    def get_all_by_pid(pid):
        rows = app.db.execute (
            '''
            SELECT *
            FROM Review
            WHERE pid = :pid
            ORDER BY review_time DESC
            ''',
            pid=pid
        )
        return [Review(*row) for row in rows]
    
    @staticmethod
    def review_exists_check(uid, pid):
        rows = app.db.execute (
            '''
            SELECT COUNT(*)
            FROM Review
            WHERE pid = :pid AND uid = :uid
            ''',
            pid=pid,
            uid=uid
        )
        return rows[0][0] # This is the count (number) of reviews where pid = pid and uid = uid
    
    @staticmethod
    def edit_review(product_id, user_id, new_review, new_rating):
        app.db.execute (
            """
            UPDATE Review
            SET
                review_content = :new_review,
                review_rating = :new_rating
            WHERE
                uid = :user_id AND pid = :product_id
            """,
            product_id=product_id,
            user_id=user_id,
            new_review=new_review,
            new_rating=new_rating
        )
        return
    
    @staticmethod
    def add_review(product_id, user_id, new_review, new_rating):
        app.db.execute (
            """
            INSERT INTO Review (uid, pid, review_time, review_content, review_rating)
            VALUES (:user_id, :product_id, current_timestamp AT TIME ZONE 'UTC', :new_review, :new_rating)
            """,
            product_id=product_id,
            user_id=user_id,
            new_review=new_review,
            new_rating=new_rating
        )
        return