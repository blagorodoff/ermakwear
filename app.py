# app.py
import os
import time
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from extensions import db, login_manager
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Collection, Category, Product, ProductImage, GalleryImage
from forms import LoginForm, CollectionForm, CategoryForm, ProductForm

app = Flask(__name__)
app.config["SECRET_KEY"] = "7ac525a5042747783a0ce2c3b13b036a6aaad9eb7e76e60d3a839e70f948ff2d"
# Если переменная окружения DATABASE_URL установлена (Render предоставит её для PostgreSQL),
# используем её. Иначе работаем с SQLite локально.
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Render передаёт строку вида postgres://..., а SQLAlchemy требует postgresql://
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Глобальная CSRF-защита
csrf = CSRFProtect(app)

# Инициализация расширений
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице."
login_manager.login_message_category = "info"

# Разрешённые расширения изображений
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads", "products")

# Создаём таблицы при первом запуске
with app.app_context():
    db.create_all()


def allowed_file(filename):
    """Проверяет, что у файла допустимое расширение."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_product_image(file, product_id, is_primary=False):
    """
    Сохраняет файл изображения в папку static/uploads/products.
    Возвращает имя файла или None при ошибке.
    """
    if not file or file.filename == "":
        return None
    if not allowed_file(file.filename):
        return None

    # Создаём папку, если её нет
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Безопасное имя файла + timestamp для уникальности
    original_filename = secure_filename(file.filename)
    timestamp = str(int(time.time()))
    filename = f"{timestamp}_{original_filename}"

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    return filename


def delete_image_file(filename):
    """Удаляет файл изображения с диска."""
    if not filename:
        return
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)


# ---------- Маршруты аутентификации ----------


@app.route("/")
def index():
    # Получаем все коллекции, отсортированные по sort_order
    collections = Collection.query.order_by(Collection.sort_order).all()
    # Получаем все категории, отсортированные по sort_order
    categories = Category.query.order_by(Category.sort_order).all()

    # Строим удобную структуру: для каждой коллекции — словарь с товарами, сгруппированными по категориям
    collections_data = []
    for coll in collections:
        # Получаем товары коллекции, отсортированные по категории и sort_order
        products = coll.products.order_by(Product.category_id, Product.sort_order).all()
        # Группируем товары по категориям
        grouped = {}
        for product in products:
            cat = product.category
            if cat is not None:
                if cat.id not in grouped:
                    grouped[cat.id] = {"category": cat, "products": []}
                grouped[cat.id]["products"].append(product)
        # Преобразуем словарь в список, упорядоченный по категориям (по sort_order)
        grouped_list = []
        for cat in categories:
            if cat.id in grouped:
                grouped_list.append(grouped[cat.id])
        # Добавляем коллекцию в общий список
        collections_data.append({"collection": coll, "grouped_products": grouped_list})

    # Вычисляем количество товаров в каждой коллекции для фильтров
    collection_counts = {coll.id: coll.products.count() for coll in collections}
    total_products = Product.query.count()

    return render_template(
        "index.html",
        collections_data=collections_data,
        categories=categories,
        collection_counts=collection_counts,
        total_products=total_products,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Вы успешно вошли.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin_dashboard"))
        else:
            flash("Неверный логин или пароль.", "error")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    return render_template("admin_dashboard.html")


# ---------- Управление коллекциями ----------


@app.route("/admin/collections")
@login_required
def admin_collections():
    collections = Collection.query.order_by(Collection.sort_order).all()
    return render_template("admin_collections.html", collections=collections)


@app.route("/admin/collections/new", methods=["GET", "POST"])
@login_required
def admin_collection_new():
    form = CollectionForm()
    if form.validate_on_submit():
        collection = Collection(
            title=form.title.data,
            description=form.description.data,
            sort_order=form.sort_order.data or 0,
        )
        db.session.add(collection)
        db.session.commit()
        flash("Коллекция создана.", "success")
        return redirect(url_for("admin_collections"))
    return render_template(
        "admin_collection_form.html", form=form, title="Новая коллекция"
    )


@app.route("/admin/collections/<int:collection_id>/edit", methods=["GET", "POST"])
@login_required
def admin_collection_edit(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    form = CollectionForm(obj=collection)
    if form.validate_on_submit():
        collection.title = form.title.data
        collection.description = form.description.data
        collection.sort_order = form.sort_order.data or 0
        db.session.commit()
        flash("Коллекция обновлена.", "success")
        return redirect(url_for("admin_collections"))
    return render_template(
        "admin_collection_form.html", form=form, title="Редактирование коллекции"
    )


@app.route("/admin/collections/<int:collection_id>/delete", methods=["POST"])
@login_required
def admin_collection_delete(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    if collection.products.count() > 0:
        flash(
            "Нельзя удалить коллекцию, в которой есть товары. Сначала удалите или переместите товары.",
            "error",
        )
        return redirect(url_for("admin_collections"))
    db.session.delete(collection)
    db.session.commit()
    flash("Коллекция удалена.", "success")
    return redirect(url_for("admin_collections"))


# ---------- Управление категориями ----------


@app.route("/admin/categories")
@login_required
def admin_categories():
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template("admin_categories.html", categories=categories)


@app.route("/admin/categories/new", methods=["GET", "POST"])
@login_required
def admin_category_new():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, sort_order=form.sort_order.data or 0)
        db.session.add(category)
        db.session.commit()
        flash("Категория создана.", "success")
        return redirect(url_for("admin_categories"))
    return render_template(
        "admin_category_form.html", form=form, title="Новая категория"
    )


@app.route("/admin/categories/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def admin_category_edit(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        category.sort_order = form.sort_order.data or 0
        db.session.commit()
        flash("Категория обновлена.", "success")
        return redirect(url_for("admin_categories"))
    return render_template(
        "admin_category_form.html", form=form, title="Редактирование категории"
    )


@app.route("/admin/categories/<int:category_id>/delete", methods=["POST"])
@login_required
def admin_category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products.count() > 0:
        flash(
            "Нельзя удалить категорию, в которой есть товары. Сначала удалите или переместите товары.",
            "error",
        )
        return redirect(url_for("admin_categories"))
    db.session.delete(category)
    db.session.commit()
    flash("Категория удалена.", "success")
    return redirect(url_for("admin_categories"))


# ---------- Управление товарами ----------


@app.route("/admin/products")
@login_required
def admin_products():
    products = Product.query.order_by(
        Product.collection_id, Product.category_id, Product.sort_order
    ).all()
    return render_template("admin_products.html", products=products)


@app.route("/admin/products/new", methods=["GET", "POST"])
@login_required
def admin_product_new():
    form = ProductForm()
    collections = Collection.query.order_by(Collection.sort_order).all()
    categories = Category.query.order_by(Category.sort_order).all()
    form.collection_id.choices = [(c.id, c.title) for c in collections]
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        product = Product(
            title=form.title.data,
            price=form.price.data,
            collection_id=form.collection_id.data,
            category_id=form.category_id.data,
            sort_order=form.sort_order.data or 0,
        )
        db.session.add(product)
        db.session.commit()

        # Обработка загруженных изображений
        files = request.files.getlist("images")
        first_uploaded = True
        for file in files:
            if file and file.filename != "":
                if allowed_file(file.filename):
                    # Первое загруженное фото делаем основным
                    filename = save_product_image(
                        file, product.id, is_primary=first_uploaded
                    )
                    if filename:
                        img = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=first_uploaded,
                            sort_order=0,
                        )
                        db.session.add(img)
                        first_uploaded = False
                    else:
                        flash(f"Не удалось сохранить файл {file.filename}", "error")
                else:
                    flash(
                        f"Файл {file.filename} имеет недопустимое расширение. Разрешены: png, jpg, jpeg, gif, webp.",
                        "error",
                    )
        db.session.commit()
        flash("Товар создан.", "success")
        return redirect(url_for("admin_product_edit", product_id=product.id))

    return render_template(
        "admin_product_form.html", form=form, title="Новый товар", product=None
    )


@app.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def admin_product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    collections = Collection.query.order_by(Collection.sort_order).all()
    categories = Category.query.order_by(Category.sort_order).all()
    form.collection_id.choices = [(c.id, c.title) for c in collections]
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        product.title = form.title.data
        product.price = form.price.data
        product.collection_id = form.collection_id.data
        product.category_id = form.category_id.data
        product.sort_order = form.sort_order.data or 0
        db.session.commit()

        # Проверяем, есть ли уже основное изображение
        has_primary = (
            ProductImage.query.filter_by(product_id=product.id, is_primary=True).first()
            is not None
        )

        files = request.files.getlist("images")
        for file in files:
            if file and file.filename != "":
                if allowed_file(file.filename):
                    # Если основного ещё нет, первое загруженное станет основным
                    make_primary = not has_primary
                    if make_primary:
                        has_primary = True  # чтобы следующие уже не были primary
                    filename = save_product_image(
                        file, product.id, is_primary=make_primary
                    )
                    if filename:
                        img = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=make_primary,
                            sort_order=0,
                        )
                        db.session.add(img)
                    else:
                        flash(f"Не удалось сохранить файл {file.filename}", "error")
                else:
                    flash(
                        f"Файл {file.filename} имеет недопустимое расширение. Разрешены: png, jpg, jpeg, gif, webp.",
                        "error",
                    )
        db.session.commit()
        flash("Товар обновлён.", "success")
        return redirect(url_for("admin_product_edit", product_id=product.id))

    return render_template(
        "admin_product_form.html",
        form=form,
        title="Редактирование товара",
        product=product,
    )


@app.route("/admin/products/<int:product_id>/delete", methods=["POST"])
@login_required
def admin_product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    # Удаляем файлы изображений
    for img in product.images:
        delete_image_file(img.filename)
    db.session.delete(product)  # каскадно удалит записи ProductImage
    db.session.commit()
    flash("Товар удалён.", "success")
    return redirect(url_for("admin_products"))


@app.route("/admin/product_images/<int:image_id>/delete", methods=["POST"])
@login_required
def admin_product_image_delete(image_id):
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id
    delete_image_file(image.filename)
    db.session.delete(image)
    db.session.commit()
    flash("Изображение удалено.", "success")
    return redirect(url_for("admin_product_edit", product_id=product_id))


@app.route("/admin/product_images/<int:image_id>/set_primary", methods=["POST"])
@login_required
def admin_product_image_set_primary(image_id):
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id
    # Сбрасываем все основные флаги для товара
    ProductImage.query.filter_by(product_id=product_id).update({"is_primary": False})
    image.is_primary = True
    db.session.commit()
    flash("Основное изображение обновлено.", "success")
    return redirect(url_for("admin_product_edit", product_id=product_id))


if __name__ == '__main__':
    app.run(debug=False)
