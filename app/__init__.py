from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .orders import bp as orders_bp
    app.register_blueprint(orders_bp)

    from .save import bp as save_bp
    app.register_blueprint(save_bp)

    from .models.purchase import bp as purchase_bp
    app.register_blueprint(purchase_bp)

    from .searchproduct import bp as searchproduct_bp
    app.register_blueprint(searchproduct_bp)

    from .review import bp as review_bp
    app.register_blueprint(review_bp)

    from .sellerreview import bp as sellerreview_bp
    app.register_blueprint(sellerreview_bp)

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)
    
    return app
