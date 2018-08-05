from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from sqlite3 import Row
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('edit', __name__)


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


def execute_update_company(result, company_id, company_name,
                           location_country, location_city, location_street, location_post_code,
                           postal_country, postal_city, postal_street, postal_post_code):

    if not result:
        result = dict()
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
    company = dict()
    company["Company_Name"] = company_name
    company["Company_ID"] = company_id
    company["Location_Country"] = location_country
    company["Location_City"] = location_city
    company["Location_Street"] = location_street
    company["Location_Post_Code"] = location_post_code
    company["Postal_Country"] = postal_country
    company["Postal_City"] = postal_city
    company["Postal_Street"] = postal_street
    company["Postal_Post_Code"] = postal_post_code
    result['company'] = company
    return result


def execute_add_company(result, company, company_name,
                        location_country="", location_city="", location_street="", location_post_code="",
                        postal_country="", postal_city="", postal_street="", postal_post_code=""):
    if not result:
        result = dict()
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
        db.commit()
        company = get_company_by_key_value("Company_Name", company_name, 1)
        result['company'] = company
    else:
        result = execute_update_company(result, company['Company_ID'], company_name,
                                        location_country, location_city, location_street, location_post_code,
                                        postal_country, postal_city, postal_street, postal_post_code)
    return result


def execute_show_company(company=None):
    contacts = None
    if company is not None and (isinstance(company, Row) or 'Company_ID' in company):
        contacts = get_contact_by_key_value("Company_ID", company["Company_ID"], 1, False)
    db = get_db()
    titles = db.execute('SELECT * FROM title').fetchall()
    companies = db.execute('SELECT Company_Name FROM customer').fetchall()
    return render_template('edit/customer.html', company=company, contacts=contacts, titles=titles, companies=companies)


@bp.route('/edit/edit_company', methods=('GET', 'POST'))
@login_required
def edit_company():
    result = dict()
    if request.method == 'POST':
        form = request.form
        action = form['action']
        if action == 'Search':
            company_name = request.form['search_name']
            if not company_name:
                result['message'] = 'Company name is required.'
            else:
                company = get_company_by_key_value("Company_Name", company_name, 1)
                if company is None:
                    result['message'] = "Company {0} doesn't exist.".format(company_name)
                else:
                    result['company'] = company
        elif action == 'Save':
            result = add_company(result, form['company'],
                                 form['location_country'], form['location_city'],
                                 form['location_street'], form['location_post_code'],
                                 form['postal_country'], form['postal_city'],
                                 form['postal_street'], form['postal_post_code'])
        elif action == 'Update':
            result = update_company(result, form['company_id'], form['company'],
                                    form['location_country'], form['location_city'],
                                    form['location_street'], form['location_post_code'],
                                    form['postal_country'], form['postal_city'],
                                    form['postal_street'], form['postal_post_code'])
        elif action == 'Remove':
            result = remove_company(result, form['company_id'])
        elif action == 'Add Contact':
            company_id = form['company_id']
            if not company_id:
                result['message'] = 'Please search the company name you want to add contact first.'
            else:
                company = get_company_by_key_value("Company_ID", company_id, 1)
                if company:
                    return execute_show_contact(None, company)
                else:
                    result['message'] = "The company you want to add contact doesn't exists."
    if 'message' in result:
        flash(result['message'])
    if 'company' in result:
        return execute_show_company(result['company'])
    return execute_show_company()


def add_company(result, company_name,
                location_country, location_city, location_street, location_post_code,
                postal_country, postal_city, postal_street, postal_post_code):
    if not result:
        result = dict()
    if not company_name:
        result['message'] = 'Please enter the company name you want to save.'
    else:
        company = get_company_by_key_value("Company_Name", company_name, 1)
        if company is not None:
            result['message'] = 'The company you want to save {0} already exists.'.format(company_name)
            new_company = dict()
            new_company["Company_Name"] = company_name
            new_company["Location_Country"] = location_country
            new_company["Location_City"] = location_city
            new_company["Location_Street"] = location_street
            new_company["Location_Post_Code"] = location_post_code
            new_company["Postal_Country"] = postal_country
            new_company["Postal_City"] = postal_city
            new_company["Postal_Street"] = postal_street
            new_company["Postal_Post_Code"] = postal_post_code
            result['company'] = new_company
        else:
            company = get_company_by_key_value("Company_Name", company_name, 0)
            result = execute_add_company(result, company, company_name,
                                         location_country, location_city, location_street, location_post_code,
                                         postal_country, postal_city, postal_street, postal_post_code)
            result['message'] = "Add company {0} completed.".format(company_name)
    return result


def remove_company(result, company_id):
    if not result:
        result = dict()
    if not company_id:
        result['message'] = 'Please search the company name you want to remove first.'
    else:
        company = get_company_by_key_value("Company_ID", company_id, 1)
        if company is None:
            result['message'] = "The company you want to remove doesn't exists."
        else:
            db = get_db()
            db.execute(
                'UPDATE customer SET State = ? WHERE Company_ID = ?',
                (0, company_id)
            )
            db.commit()
            result['message'] = "Remove company {0} completed.".format(company['Company_Name'])
    return result


def update_company(result, company_id, company_name,
                   location_country, location_city, location_street, location_post_code,
                   postal_country, postal_city, postal_street, postal_post_code):
    if not result:
        result = dict()
    if not company_id:
        result['message'] = 'Please search the company name you want to update first.'
    else:
        company = get_company_by_key_value("Company_ID", company_id)
        if company is None:
            result['message'] = "The company you want to update doesn't exists."
        else:
            if not company_name:
                result['message'] = "Please enter the company name you want to update."
            else:
                cur_company = get_company_by_key_value("Company_Name", company_name, 1)
                if cur_company is not None:
                    result['message'] = "The company name " + company_name + " you want to update is already used."
                else:
                    result = execute_update_company(result, company_id, company_name,
                                                    location_country, location_city, location_street,
                                                    location_post_code,
                                                    postal_country, postal_city, postal_street, postal_post_code)
                    result['message'] = "Update company " + company_name + " completed."
    return result


def get_contact_by_key_value(key, value, state=None, single=True):
    if key is None:
        return None
    if value is None:
        return None
    db = get_db()
    if state is not None:
        result = db.execute(
            'SELECT * FROM contact WHERE ' + key + ' = ? AND State = ?', (value, state)
        ).fetchall()
    else:
        result = db.execute(
            'SELECT * FROM contact WHERE ' + key + ' = ?', (value,)
        ).fetchall()
    if len(result) == 0:
        return None
    if single:
        return result[0]
    return result


def execute_show_contact(contact=None, company=None):
    db = get_db()
    titles = db.execute('SELECT * FROM title').fetchall()
    contacts = db.execute('SELECT Contact_Name FROM contact').fetchall()
    return render_template('edit/contact.html', titles=titles, contact=contact, company=company, contact_names=contacts)


@bp.route('/edit/edit_contact', methods=('GET', 'POST'))
@login_required
def edit_contact():
    contact = None
    company = None
    if request.method == 'POST':
        message = None
        form = request.form
        action = form['action']
        if action == 'Search':
            contact_name = form['search_name']
            contact = get_contact_by_key_value("Contact_Name", contact_name, 1)
            if contact is None:
                message = "The contact {0} you want to search doesn't exists.".format(contact_name)
        elif action == 'Edit':
            contact_id = form['contact_id']
            if not contact_id:
                message = "Contact_ID name is required."
            else:
                contact = get_contact_by_key_value("Contact_ID", contact_id, 1)
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
        if message is not None:
            flash(message)
    if contact:
        company = get_company_by_key_value("Company_ID", contact["Company_ID"])
    return execute_show_contact(contact, company)


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
            result = dict()
            result = execute_add_company(result, company, company_name)
            company_id = result['company']['Company_ID']
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
            (title_id, contact_name, company_id, role,
             location_country, location_city, location_street, location_post_code,
             email, phone_work, phone_cell, phone_home, notes))
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
                (title_id, contact_name, company_id, role,
                 location_country, location_city, location_street, location_post_code,
                 email, phone_work, phone_cell, phone_home, notes, 1,
                 contact['Contact_ID']))
            db.commit()
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
    if not company_name:
        company_id = ""
    else:
        company = get_company_by_key_value("Company_Name", company_name)
        if company is None or company["State"] == 0:
            result = dict()
            result = execute_add_company(result, company, company_name)
            company_id = result['company']['Company_ID']
        else:
            company_id = company['Company_ID']
    db = get_db()
    db.execute(
        'UPDATE contact SET '
        'Title_ID = ?, Contact_Name = ?, Company_ID = ?, Role = ?, '
        'Location_Country = ?, Location_City = ?, Location_Street = ?, Location_Post_Code = ?,'
        'Email = ?, Phone_Work = ?, Phone_Cell = ?, Phone_Home = ?, Notes = ?, State = ? '
        'WHERE Contact_ID = ?',
        (title_id, contact_name, company_id, role,
         location_country, location_city, location_street, location_post_code,
         email, phone_work, phone_cell, phone_home, notes, 1,
         contact_id))
    db.commit()
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
