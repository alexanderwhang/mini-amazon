from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
import re
from .. import login

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, seller, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.seller = seller
        self.balance = "{:0.2f}".format(balance)

    #method for finding a user given an email and password. Returns a User object
    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, address, seller, balance
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

    #returns a boolean if an email is already in the Users table
    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    #adds a user to the Users table. returns a User object
    @staticmethod
    def register(email, password, firstname, lastname, address):
        try:
            rows = app.db.execute("""
            INSERT INTO Users(email, password, firstname, lastname, address, seller, balance)
            VALUES(:email, :password, :firstname, :lastname, :address, False, 0)
            RETURNING id
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

    #returns a User object given their user id
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, seller, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    #update a user's personal information. Returns an updated User object
    @staticmethod
    def updateUser(id, newEmail, newPassword, newAddress, newFirstName, newLastName, newBalance, passwordConfirmation):
        #get the user's old information
        rows = app.db.execute("""
            SELECT password, email, address, firstname, lastname, balance
            FROM Users
            where id = :id
            """,
            id=id)
        oldpassword = rows[0][0]
        oldemail = rows[0][1]
        oldaddress = rows[0][2]
        oldfirstname = rows[0][3]
        oldlastname = rows[0][4]
        oldbalance = rows[0][5] 

        #check if a user has entered the correct password. if the PW is incorrect, the update is aborted
        if not check_password_hash(oldpassword, passwordConfirmation):
            # incorrect password
            raise BadUpdateException("Incorrect Password")

        #check that the new email is:
        #   - not the same as the old email
        #   - not an email that exists in the database for a different user
        if len(newEmail) > 0:
            if not re.fullmatch(email_regex, newEmail):
                raise BadUpdateException("Invalid email")
            if newEmail == oldemail:
                raise BadUpdateException("New email can't be old email")
            if User.email_exists(newEmail):
                raise BadUpdateException("Email already exists")
            app.db.execute("UPDATE Users SET email = :newEmail WHERE id = :id",id=id, newEmail=newEmail)

        #check that the new password is:
        #   - not the same as the old password
        if len(newPassword) > 0:
            if check_password_hash(oldpassword, newPassword):
                raise BadUpdateException("New password can't be old password")
            app.db.execute("UPDATE Users SET password = :newPShash WHERE id = :id",id=id, newPShash=generate_password_hash(newPassword))
        
        #check that the new address is:
        #   - not the same as the old address
        if len(newAddress) > 0:
            if oldaddress == newAddress:
                raise BadUpdateException("New address can't be old address")
            app.db.execute("UPDATE Users SET address = :newAddress WHERE id = :id",id=id, newAddress=newAddress)
        
        #check that the new first name is:
        #   - not the same as the old first name
        if len(newFirstName) > 0:
            if oldfirstname == newFirstName:
                raise BadUpdateException("New first name can't be old first name")
            app.db.execute("UPDATE Users SET firstname = :newFirstName WHERE id = :id",id=id, newFirstName=newFirstName)
        
        #check that the new last name is:
        #   - not the same as the old last name
        if len(newLastName) > 0:
            if oldlastname == newLastName:
                raise BadUpdateException("New last name can't be old last name")
            app.db.execute("UPDATE Users SET lastname = :newLastName WHERE id = :id",id=id, newLastName=newLastName)
        
        #check that the new balance is:
        #   - a valid float
        #   - a positive number

        if len(newBalance) > 0:
            try:
                newBalance = float(newBalance)
            except Exception:
                raise BadUpdateException("New balance must be a number")

            if newBalance < 0:
                raise BadUpdateException("New balance can't be negative")
            app.db.execute("UPDATE Users SET balance = :newBalance WHERE id = :id",id=id, newBalance=newBalance)

        return User.get(id)

#exception for when a user tries to update their information and fails
class BadUpdateException(BaseException):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg
    def toString(self):
        return self.msg
