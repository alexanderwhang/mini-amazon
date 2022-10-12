from flask import Blueprint
bp = Blueprint('product', __name__)

@bp.route('/productpage')
def productpage():
    return render_template('productpage.html')