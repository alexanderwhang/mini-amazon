from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, seller, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.seller = seller
        self.balance = "{:0.2f}".format(balance)

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, user_id, email, firstname, lastname, address, seller, balance
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
            INSERT INTO Users(email, password, firstname, lastname, address, seller, balance)
            VALUES(:id, :email, :password, :firstname, :lastname, :address, False, 0)
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
SELECT user_id, email, firstname, lastname, address, seller, balance
FROM Users
WHERE user_id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def updateUser(id, newEmail, newPassword, newAddress, newFirstName, newLastName, newBalance, passwordConfirmation):
        rows = app.db.execute("""
            SELECT password, email, address, firstname, lastname, balance
            FROM Users
            where user_id = :id
            """,
            id=id)
        oldpassword = rows[0][0]
        oldemail = rows[0][1]
        oldaddress = rows[0][2]
        oldfirstname = rows[0][3]
        oldlastname = rows[0][4]
        oldbalance = rows[0][5] 

        if not check_password_hash(oldpassword, passwordConfirmation):
            # incorrect password
            raise BadUpdateException("Incorrect Password")


        query = []
        if len(newEmail) > 0:
            if newEmail == oldemail:
                raise BadUpdateException("New email can't be old email")
            if User.email_exists(newEmail):
                raise BadUpdateException("Email already exists")
            query.append(f"email = '{newEmail}'")
        if len(newPassword) > 0:
            if check_password_hash(oldpassword, newPassword):
                raise BadUpdateException("New password can't be old password")
            query.append(f"password = '{generate_password_hash(newPassword)}' ")
        if len(newAddress) > 0:
            if oldaddress == newAddress:
                raise BadUpdateException("New address can't be old address")
            query.append(f"address = '{newAddress}'")
        if len(newFirstName) > 0:
            if oldfirstname == newFirstName:
                raise BadUpdateException("New first name can't be old first name")
            query.append(f"firstname = '{newFirstName}'")
        if len(newLastName) > 0:
            if oldlastname == newLastName:
                raise BadUpdateException("New last name can't be old last name")
            query.append(f"lastname = '{newLastName}'")
        if len(newBalance) > 0:
            try:
                newBalance = int(newBalance)
            except Exception:
                raise BadUpdateException("New balance must be a number")

            if newBalance < 0:
                raise BadUpdateException("New balance can't be negative")
            query.append(f"balance = {newBalance}")
        query = ", ".join(query)
        query = "UPDATE Users SET " + query + f" WHERE id = {id};"

        app.db.execute(query)   

        return User.get(id)

class BadUpdateException(BaseException):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg
    def toString(self):
        return self.msg
