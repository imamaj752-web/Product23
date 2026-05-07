from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import init_db
from action_db import *

app = Flask(__name__)
app.secret_key = '123'
init_db()


def is_logged():
    return 'company_name' in session


def current_company():
    name_company = session.get('company_name')
    if not name_company:
        return None
    return get_company_by_name(name_company)


@app.route('/', methods=['GET', 'POST'])
def index():
    if not is_logged():
        return redirect(url_for('login'))

    company = current_company()

    if request.method == 'POST':
        name = request.form.get('name').lower()
        price = float(request.form.get('price'))
        category = request.form.get('category').lower()

        if product_exist(name, company.id):
            flash('Такой товар уже есть')
        else:
            add_product(name, price, category, company.id)
            flash('Товар +')
        return redirect(url_for('index'))

    all_categories = get_all_categories(company.id)
    choice_category = request.args.get('category', 'all')

    if choice_category == 'all':
        products = get_all_products(company.id)
    else:
        products = get_product_by_category(choice_category, company.id)

    return render_template('index.html', products=products, categories=all_categories, choice_category=choice_category)


@app.route('/delete/<name>')
def delete(name):
    company = current_company()
    delete_product(name, company.id)
    flash(f'Товар {name} видалено')
    return redirect(url_for('index'))

@app.route('/edit/<name>', methods=['GET', 'POST'])
def edit(name):
    if not is_logged():
        return redirect(url_for('login'))

    company = current_company()
    product = get_product_by_name(name, company.id)

    if not product:
        flash("Товар не найдено")
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            new_price = float(request.form.get('price'))
            new_category = request.form.get('category').lower()

            update_product(name, new_price, new_category, company.id)
            flash(f'Товар "{name}" обновлено')
            return redirect(url_for('index'))
        except ValueError:
            flash("цена должна будь числом")

    return render_template('edit.html', product=product)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name_company = request.form.get('name_company').lower()
        password = request.form.get('password')

        if company_exists(name_company):
            flash('Такая компания уже есть')
            return redirect(url_for('register'))
        else:
            password_hash = generate_password_hash(password)
            add_company(name_company, password_hash)
            flash(f'Компания {name_company} зарегана')
            return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name_company = request.form.get('name_company').lower()
        password = request.form.get('password')

        if not company_exists(name_company):
            flash(f'Компания {name_company} не существует')
            return redirect(url_for('login'))

        company = get_company_by_name(name_company)
        if not check_password_hash(company.password, password):
            flash(f'Пароль НЕкорект')
            return redirect(url_for('login'))

        session['company_name'] = company.name
        flash(f'Поздравляем {company.name}')
        return redirect(url_for('index'))

    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)