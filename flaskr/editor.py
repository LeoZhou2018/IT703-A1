from flask import (
    Blueprint, render_template
)

from flaskr.auth import login_required

bp = Blueprint('edit', __name__)


@bp.route('/edit/customer')
@login_required
def show_customer():
    return render_template('edit/customer.html')


@bp.route('/edit/contact')
@login_required
def show_contact():
    return render_template('edit/contact.html')