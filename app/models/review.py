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
    def edit_review(review_id, new_review):
        app.db.execute (
            """
            UPDATE Review
            SET
                review_content = :new_review
            WHERE
                id = :review_id
            """,
            review_id=review_id,
            new_review=new_review
        )
        return
        
    # @staticmethod
    # def get(id):
    #     rows = app.db.execute('''
    #     SELECT id, uid, pid, review_time, review_content
    #     FROM Review
    #     WHERE id = :id
    #     ''',
    #                           id=id)
    #     return Review(*(rows[0])) if rows else None

    # @staticmethod
    # def get_all_by_uid_since(uid, since):
    #     rows = app.db.execute('''
    # SELECT id, uid, pid, review_time, review_content
    # FROM Review
    # WHERE uid = :uid
    # AND review_time >= :since
    # ORDER BY review_time DESC
    # ''',
    #                               uid=uid,
    #                               since=since)
    #         return [Review(*row) for row in rows]