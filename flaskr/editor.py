from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('edit', __name__)


@bp.route('/')
@login_required
def show_customer():
    return render_template('edit/customer.html')


@bp.route('/edit/contact')
@login_required
def show_contact():
    return render_template('edit/contact.html')


@bp.route('/edit/search', methods=('GET', 'POST'))
@login_required
def search():
    """search for company information."""
    if request.method == 'POST':
        company_name = request.form['search_name']
        error = None

        if not company_name:
            error = 'Company name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            company = db.execute(
                'SELECT * FROM customer WHERE Company_Name = company_name'
            ).fetchall()
            if len(company) == 0:
                flash("Company {0} doesn't exist.".format(company_name))
    return render_template('edit/customer.html', post=company)
