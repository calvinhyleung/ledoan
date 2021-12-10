from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from .. import bcrypt
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, AddProductForm
from ..models import User, Product

users = Blueprint("users", __name__)

""" ************ User Management views ************ """

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("products.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        user.save()

        return redirect(url_for("users.login"))

    return render_template("register.html", title="Register", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("products.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()

        if user is not None and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            return redirect(url_for("users.account"))
        else:
            flash("Login failed. Check your username and/or password")
            return redirect(url_for("users.login"))

    return render_template("login.html", title="Login", form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("products.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    username_form = UpdateUsernameForm()
    if username_form.validate_on_submit():
        current_user.modify(username=username_form.username.data)
        current_user.save()
        return redirect(url_for("users.account"))

    add_product_form = AddProductForm()
    if add_product_form.validate_on_submit():
        img = add_product_form.image.data
        filename = secure_filename(img.filename)
        content_type = f'images/{filename[-3:]}'
        # item = Item(name=add_product_form.name.data, 
        #             price=add_product_form.price.data, 
        #             description=add_product_form.description.data,
        #             ingredients=add_product_form.ingredients.data,
        #             amount=add_product_form.amount.data,
        #             )
        product = Product()
        product.name = add_product_form.name.data
        product.price = add_product_form.price.data
        product.description = add_product_form.description.data
        product.ingredients = add_product_form.ingredients.data
        product.amount = add_product_form.amount.data
        product.image.put(img.stream, content_type=content_type)
        product.save()
        return redirect(url_for('products.index'))

    return render_template(
        "account.html",
        title="Account",
        username_form=username_form,
        add_product_form=add_product_form
    )