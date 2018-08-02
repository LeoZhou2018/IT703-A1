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


@bp.route('/edit/edit_company', methods=('GET', 'POST'))
@login_required
def edit_company():
    """edit company information."""
    error = None
    if request.method == 'POST':
        action = request.form['action']
        if not action:
            flash('Action type is required.')
        else:
            if action == 'Save':
                '''Add new company'''
                error = add_company(request.form['company'],
                                    request.form['location_country'],
                                    request.form['location_city'],
                                    request.form['location_street'],
                                    request.form['location_post_code'],
                                    request.form['postal_country'],
                                    request.form['postal_city'],
                                    request.form['postal_street'],
                                    request.form['postal_post_code'],
                                    )
            elif action == 'Update':
                '''Update company information'''
                error = update_company(request.form['company_id'],
                                       request.form['company'],
                                       request.form['location_country'],
                                       request.form['location_city'],
                                       request.form['location_street'],
                                       request.form['location_post_code'],
                                       request.form['postal_country'],
                                       request.form['postal_city'],
                                       request.form['postal_street'],
                                       request.form['postal_post_code'],
                                       )
            elif action == 'Remove':
                '''Remove company'''
                error = remove_company(request.form['company_id'])
            elif action == 'Add Contact':
                '''Add contact to company'''
                company_id = request.form['company_id']
                if not company_id:
                    error = 'Please search the company name you want to add contact first.'
                else:
                    db = get_db()
                    company = db.execute(
                        'SELECT * FROM customer WHERE Company_ID = ?', (company_id,)
                    ).fetchall()
                    if len(company) == 0:
                        error = "The company you want to add contact doesn't exists."
                    else:
                        return render_template('edit/contact.html',
                                               company_id=company_id,
                                               company_name=company[0]['Company_Name'])
            else:
                '''Unsupported operation'''
                error = "Unsupported operation: {0}".format(action)
    flash(error)
    return render_template('edit/customer.html')


def add_company(company_name,
                location_country,
                location_city,
                location_street,
                location_post_code,
                postal_country,
                postal_city,
                postal_street,
                postal_post_code
                ):
    if not company_name:
        error = 'Please enter the company name you want to save.'
    else:
        db = get_db()
        company = db.execute(
            'SELECT * FROM customer WHERE Company_Name = ?', (company_name,)
        ).fetchall()
        if len(company) == 0:
            db = get_db()
            db.execute(
                'INSERT INTO customer ('
                'Company_Name, '
                'Location_Country, '
                'Location_City,'
                'Location_Street, '
                'Location_Post_Code, '
                'Postal_Country, '
                'Postal_City, '
                'Postal_Street, '
                'Postal_Post_Code)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (company_name,
                 location_country,
                 location_city,
                 location_street,
                 location_post_code,
                 postal_country,
                 postal_city,
                 postal_street,
                 postal_post_code)
            )
            db.commit()
            error = "Add company {0} completed.".format(company_name)
        else:
            cur_company = company[0]
            if cur_company['State'] == 1:
                error = 'The company you want to save {0} already exists.'.format(company_name)
            else:
                execute_update(cur_company['Company_ID'],
                               company_name,
                               location_country,
                               location_city,
                               location_street,
                               location_post_code,
                               postal_country,
                               postal_city,
                               postal_street,
                               postal_post_code
                               )
                error = "Add company {0} completed.".format(company_name)
    return error


def remove_company(company_id):
    if not company_id:
        error = 'Please search the company name you want to remove first.'
    else:
        db = get_db()
        company = db.execute(
            'SELECT * FROM customer WHERE Company_ID = ?', (company_id,)
        ).fetchall()
        if len(company) == 0:
            error = "The company you want to remove doesn't exists."
        else:
            db = get_db()
            db.execute(
                'UPDATE customer SET State = ? WHERE Company_ID = ?',
                (0, company_id)
            )
            db.commit()
            error = "Remove company {0} completed.".format(company[0]['Company_Name'])
    return error


def update_company(company_id,
                   company_name,
                   location_country,
                   location_city,
                   location_street,
                   location_post_code,
                   postal_country,
                   postal_city,
                   postal_street,
                   postal_post_code):
    if not company_id:
        error = 'Please search the company name you want to update first.'
    else:
        db = get_db()
        company = db.execute(
            'SELECT * FROM customer WHERE Company_ID = ?', (company_id,)
        ).fetchall()
        if len(company) == 0:
            error = "The company you want to update doesn't exists."
        else:
            if not company_name:
                error = "Please enter the company name you want to update."
            else:
                execute_update(company_id,
                               company_name,
                               location_country,
                               location_city,
                               location_street,
                               location_post_code,
                               postal_country,
                               postal_city,
                               postal_street,
                               postal_post_code)
                error = "Update company {0} completed.".format(request.form['company'])
    return error


def execute_update(company_id,
                   company_name,
                   location_country,
                   location_city,
                   location_street,
                   location_post_code,
                   postal_country,
                   postal_city,
                   postal_street,
                   postal_post_code):

    db = get_db()
    db.execute(
        'UPDATE customer SET '
        'Company_Name = ?,'
        'Location_Country = ?,'
        'Location_City = ?,'
        'Location_Street = ?,'
        'Location_Post_Code = ?,'
        'Postal_Country = ?,'
        'Postal_City = ?,'
        'Postal_Street = ?,'
        'Postal_Post_Code = ?,'
        'State = ?'
        'WHERE Company_ID = ?',
        (company_name,
         location_country,
         location_city,
         location_street,
         location_post_code,
         postal_country,
         postal_city,
         postal_street,
         postal_post_code,
         1,
         company_id)
    )
    db.commit()


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
                'SELECT * FROM customer WHERE Company_Name = ? AND State = ?', (company_name, 1)
            ).fetchall()
            if len(company) == 0:
                flash("Company {0} doesn't exist.".format(company_name))
            else:
                return render_template('edit/customer.html', company=company[0])
    return render_template('edit/customer.html')


def get_contacts_by_company_id(company_id):
    contacts = None
    if company_id:
        db = get_db()
        contacts = db.execute(
            'SELECT * FROM contact WHERE Company_ID = ? AND State = ?', (company_id, 1)
        ).fetchall()
    return contacts


@bp.route('/edit/edit_contact', methods=('GET', 'POST'))
@login_required
def edit_contact():
    """edit contact information."""
    return render_template('edit/contact.html')
