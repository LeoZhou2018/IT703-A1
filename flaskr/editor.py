from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('edit', __name__)


def execute_show_company(company=None):
    contacts = None
    if company is not None:
        contacts = get_contact_by_key_value("Company_ID", company["Company_ID"], 1, False)
    return render_template('edit/customer.html', company=company, contacts=contacts)


@bp.route('/edit/show_company')
@login_required
def show_company():
    return execute_show_company()


@bp.route('/edit/search_company', methods=('GET', 'POST'))
@login_required
def search_company():
    company = None
    error = None
    if request.method == 'POST':
        company_name = request.form['search_name']
        if not company_name:
            error = 'Company name is required.'
        else:
            company = get_company_by_key_value("Company_Name", company_name, 1)
            if company is None:
                error = "Company {0} doesn't exist.".format(company_name)
    if error:
        flash(error)
    return execute_show_company(company)


@bp.route('/edit/edit_company', methods=('GET', 'POST'))
@login_required
def edit_company():
    if request.method == 'POST':
        error = None
        form = request.form
        action = form['action']
        if action == 'Save':
            error = add_company(form['company'],
                                form['location_country'], form['location_city'],
                                form['location_street'], form['location_post_code'],
                                form['postal_country'], form['postal_city'],
                                form['postal_street'], form['postal_post_code'])
        elif action == 'Update':
            error = update_company(form['company_id'], form['company'],
                                   form['location_country'], form['location_city'],
                                   form['location_street'], form['location_post_code'],
                                   form['postal_country'], form['postal_city'],
                                   form['postal_street'], form['postal_post_code'])
        elif action == 'Remove':
            error = remove_company(form['company_id'])
        elif action == 'Add Contact':
            company_id = form['company_id']
            if not company_id:
                error = 'Please search the company name you want to add contact first.'
            else:
                company = get_company_by_key_value("Company_ID", company_id, 1)
                if company:
                    return execute_show_contact(None, company)
                else:
                    error = "The company you want to add contact doesn't exists."
        flash(error)
    return render_template('edit/customer.html')


def add_company(company_name,
                location_country, location_city, location_street, location_post_code,
                postal_country, postal_city, postal_street, postal_post_code):
    if not company_name:
        message = 'Please enter the company name you want to save.'
    else:
        company = get_company_by_key_value("Company_Name", company_name)
        if company is not None and company["State"] == 1:
            message = 'The company you want to save {0} already exists.'.format(company_name)
        else:
            execute_add_company(company, company_name,
                                location_country, location_city, location_street, location_post_code,
                                postal_country, postal_city, postal_street, postal_post_code)
            message = "Add company {0} completed.".format(company_name)
    return message


def execute_add_company(company, company_name,
                        location_country, location_city, location_street, location_post_code,
                        postal_country, postal_city, postal_street, postal_post_code):
    if company is None:
        db = get_db()
        db.execute(
            'INSERT INTO customer ('
            'Company_Name, '
            'Location_Country, Location_City, Location_Street, Location_Post_Code, '
            'Postal_Country, Postal_City, Postal_Street, Postal_Post_Code)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (company_name,
             location_country, location_city, location_street, location_post_code,
             postal_country, postal_city, postal_street, postal_post_code))
        company_id = db.lastrowid
        db.commit()
    else:
        execute_update_company(company['Company_ID'], company_name,
                               location_country, location_city, location_street, location_post_code,
                               postal_country, postal_city, postal_street, postal_post_code)
        company_id = company['Company_ID']
    return company_id


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


def update_company(company_id, company_name,
                   location_country, location_city, location_street, location_post_code,
                   postal_country, postal_city, postal_street, postal_post_code):
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
                execute_update_company(company_id, company_name,
                                       location_country, location_city, location_street, location_post_code,
                                       postal_country, postal_city, postal_street, postal_post_code)
                error = "Update company {0} completed.".format(request.form['company'])
    return error


def get_company_by_key_value(key, value, state=None):
    if not key:
        return None
    if not value:
        return None
    db = get_db()
    if state is not None:
        result = db.execute(
            'SELECT * FROM customer WHERE ' + key + ' = ? AND State = ?', (value, state)
        ).fetchall()
    else:
        result = db.execute(
            'SELECT * FROM customer WHERE ' + key + ' = ?', (value,)
        ).fetchall()
    if len(result) == 0:
        return None
    return result[0]


def execute_update_company(company_id, company_name,
                           location_country, location_city, location_street, location_post_code,
                           postal_country, postal_city, postal_street, postal_post_code):

    db = get_db()
    db.execute(
        'UPDATE customer SET '
        'Company_Name = ?,'
        'Location_Country = ?, Location_City = ?, Location_Street = ?, Location_Post_Code = ?,'
        'Postal_Country = ?, Postal_City = ?, Postal_Street = ?, Postal_Post_Code = ?,'
        'State = ?'
        'WHERE Company_ID = ?',
        (company_name,
         location_country, location_city, location_street, location_post_code,
         postal_country, postal_city, postal_street, postal_post_code,
         1, company_id)
    )
    db.commit()


def get_contacts_by_company_id(company_id):
    contacts = None
    if company_id:
        db = get_db()
        contacts = db.execute(
            'SELECT * FROM contact WHERE Company_ID = ? AND State = ?', (company_id, 1)
        ).fetchall()
    return contacts


def get_contact_by_key_value(key, value, state=None, single=True):
    if key is None:
        return None
    if value is None:
        return None
    db = get_db()
    if state is not None:
        result = db.execute(
            'SELECT * FROM contact WHERE ? = ? AND State = ?', (key, value, state)
        ).fetchall()
    else:
        result = db.execute(
            'SELECT * FROM contact WHERE ? = ?', (key, value)
        ).fetchall()
    if len(result) == 0:
        return None
    if single:
        return result[0]
    return result


def execute_show_contact(contact=None, company=None):
    db = get_db()
    titles = db.execute('SELECT * FROM title').fetchall()
    return render_template('edit/contact.html', titles=titles, contact=contact, company=company)


@bp.route('/edit/show_contact')
@login_required
def show_contact():
    return execute_show_contact()


@bp.route('/edit/edit_contact', methods=('GET', 'POST'))
@login_required
def edit_contact():
    contact = None
    company = None
    if request.method == 'POST':
        message = None
        form = request.form
        action = form['action']
        if action == 'New':
            show_contact()
        elif action == 'Save':
            message = add_contact(form['title'], form['contact_name'], form['company'], form['role'],
                                  form['location_country'], form['location_city'], form['location_street'],
                                  form['location_post_code'], form['phone_work'], form['phone_cell'],
                                  form['phone_home'], form['email'], form['notes'])
        elif action == 'Update':
            message = update_contact(form['title'], form['contact_id'], form['contact_name'], form['company'],
                                     form['role'], form['location_country'], form['location_city'],
                                     form['location_street'], form['location_post_code'], form['phone_work'],
                                     form['phone_cell'], form['phone_home'], form['email'], form['notes'])
        elif action == 'Remove':
            message = remove_contact(form['contact_id'])
        flash(message)
    if contact:
        company = get_contacts_by_company_id(contact["Company_ID"])
    show_contact(contact, company)


def check_title(title_id):
    db = get_db()
    result = db.execute(
        'SELECT * FROM title WHERE Title_ID = ?', (title_id,)
    ).fetchall()
    if len(result) == 0:
        return False
    return True


def add_contact(title_id, contact_name, company_name, role,
                location_country, location_city, location_street, location_post_code,
                phone_work, phone_cell, phone_home, email, notes):
    if not contact_name:
        return "Please enter the contact name you want to save."
    result = check_title(title_id)
    if not result:
        return "Title id incorrect."
    db = get_db()
    if company_name is None:
        company_id = None
    else:
        company = get_company_by_key_value("Company_Name", company_name)
        if company is None or company["State"] == 0:
            company_id = execute_add_company(company, company_name)
        else:
            company_id = company['Company_ID']
    result = db.execute(
        'SELECT * FROM contact WHERE Contact_Name = ? AND Company_ID = ?', (contact_name, company_id)
    ).fetchall()
    if len(result) == 0:
        db.execute(
            'INSERT INTO contact ('
            'Title_ID, Contact_Name, Company_ID, Role, '
            'Location_Country, Location_City, Location_Street, Location_Post_Code, '
            'Email, Phone_Work, Phone_Cell, Phone_Home, Notes)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (title_id, contact_name, company_name, role,
             location_country, location_city, location_street, location_post_code,
             phone_work, phone_cell, phone_home, email, notes))
        db.commit()
    else:
        contact = result[0]
        if contact['State'] == 1 and contact['Title_ID'] == title_id:
            return "The contact"+format(contact_name)+"ou want to save to "+format(company_name)+" already exists."
        else:
            db.execute(
                'UPDATE contact SET '
                'Title_ID = ?, Contact_Name = ?, Company_ID = ?, Role = ?, '
                'Location_Country = ?, Location_City = ?, Location_Street = ?, Location_Post_Code = ?,'
                'Email = ?, Phone_Work = ?, Phone_Cell = ?, Phone_Home = ?, Notes = ?, State = ?'
                'WHERE Contact_ID = ?',
                (title_id, contact_name, company_name, role,
                 location_country, location_city, location_street, location_post_code,
                 phone_work, phone_cell, phone_home, email, notes, 1,
                 company_id))
    return "Add contact {0} completed.".format(contact_name)


def update_contact(title_id, contact_id, contact_name, company_name, role,
                   location_country, location_city, location_street, location_post_code,
                   phone_work, phone_cell, phone_home, email, notes):
    if not contact_name or not contact_id:
        return "Please enter the contact name you want to save."
    result = check_title(title_id)
    if not result:
        return "Title id incorrect."
    contact = get_contact_by_key_value('Contact_ID', contact_id)
    if contact is None:
        return "The company you want to update doesn't exists."
    if company_name is None:
        company_id = None
    else:
        company = get_company_by_key_value("Company_Name", company_name)
        if company is None or company["State"] == 0:
            company_id = execute_add_company(company, company_name)
        else:
            company_id = company['Company_ID']
    db = get_db()
    db.execute(
        'UPDATE contact SET '
        'Title_ID = ?, Contact_Name = ?, Company_ID = ?, Role = ?, '
        'Location_Country = ?, Location_City = ?, Location_Street = ?, Location_Post_Code = ?,'
        'Email = ?, Phone_Work = ?, Phone_Cell = ?, Phone_Home = ?, Notes = ?, State = ?'
        'WHERE Contact_ID = ?',
        (title_id, contact_name, company_name, role,
         location_country, location_city, location_street, location_post_code,
         phone_work, phone_cell, phone_home, email, notes, 1,
         company_id))
    return "Update contact {0} completed.".format(contact_name)


def remove_contact(contact_id):
    if not contact_id:
        return "Please select the contact name you want to remove first."
    contact = get_contact_by_key_value('Contact_ID', contact_id)
    if contact is None or contact['State'] == 0:
        return "The company you want to remove doesn't exists."
    db = get_db()
    db.execute(
        'UPDATE contact SET State = ? WHERE Contact_ID = ?',
        (0, contact_id))
    db.commit()
    return "Remove contact {0} completed.".format(contact['Contact_Name'])
