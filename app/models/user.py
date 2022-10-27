from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.balance = "{:0.2f}".format(balance)

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, user_id, email, firstname, lastname, address, balance
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname, address):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname, address, balance)
VALUES(:email, :password, :firstname, :lastname, :address, 0)
RETURNING user_id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname, address=address)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT user_id, email, firstname, lastname, address, balance
FROM Users
WHERE user_id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def updateUser(id, newEmail, newPassword, newAddress, newFirstName, newLastName, newBalance, passwordConfirmation):
        rows = app.db.execute("""
            SELECT password
            FROM Users
            where user_id = :id
            """,
            id=id)
        if not check_password_hash(rows[0][0], passwordConfirmation):
            # incorrect password
            print("incorrect pw")
            return None

        query = []
        if len(newEmail) > 0:
            query.append(f"email = '{newEmail}'")
        if len(newPassword) > 0:
            query.append(f"password = '{generate_password_hash(newPassword)}' ")
        if len(newAddress) > 0:
            query.append(f"address = '{newAddress}'")
        if len(newFirstName) > 0:
            query.append(f"firstname = '{newFirstName}'")
        if len(newLastName) > 0:
            query.append(f"lastname = '{newLastName}'")
        if len(newBalance) > 0:
            assert int(newBalance) >= 0
            query.append(f"balance = {int(newBalance)}")
        query = ", ".join(query)
        query = "UPDATE Users SET " + query + f" WHERE user_id = {id};"
        print(query)
        app.db.execute(query)   

        return User.get(id)
