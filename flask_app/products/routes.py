from flask import Blueprint, render_template, url_for, redirect, request, flash, Markup
from flask_login import current_user,  login_required
from ..models import User, Product, Reservation, Status
from ..forms import ReservationForm, ChangeStatusForm

import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import json

products = Blueprint("products", __name__)

@products.route("/", methods=["GET", "POST"])
def index():
    products = Product.objects()
    return render_template("index.html", products=products)

@products.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

@products.route("/products/<product_name>", methods=["GET", "POST"])
def product_detail(product_name):
    product = Product.objects(name=product_name).first()
    form = ReservationForm()      
    form.amount.choices = [(i+1, str(i+1)) for i in range(product.get_limit())]
    if current_user.is_authenticated:
        user_id = User.objects(username=current_user.username).get()
        existing_reservation = Reservation.objects(user=user_id, product=product).first()
        
        if existing_reservation is not None : 
            # print(existing_reservation.product.name)
            form.submit.label.text = "Update"
        if form.validate_on_submit():
            if existing_reservation is not None : 
                if existing_reservation.status == "Pending": 
                    existing_reservation.modify(amount = form.amount.data)
                    existing_reservation.save()
            else :  
                reservation = Reservation(
                    user = current_user._get_current_object(),
                    product = product,
                    amount = form.amount.data,
                    status = Status.PENDING.value
                )
                reservation.save()
            return redirect(url_for("products.reservation"))
    return render_template("product_detail.html", product=product, form=form)

@products.route("/reservation", methods=["GET", "POST"])
@login_required
def reservation():
    user_id = User.objects(username=current_user.username).get()
    if current_user.username == "admin":
        reservations = Reservation.objects()
    else:
        reservations = Reservation.objects(user=user_id)
    plot = plot_by_product()
    plot2 = plot_by_user()
    return render_template("reservation.html",reservations=reservations, plot=plot)

@products.route("/reservation_detail/<product_name>/<user_name>", methods=["GET", "POST"])
@login_required
def reservation_detail(product_name, user_name):
    if current_user.username == "admin":
        form = ChangeStatusForm()
        user_id = User.objects(username=user_name).get()
        product_id = Product.objects(name=product_name).get()
        user = User.objects(username=user_name).first()
        product = Product.objects(name=product_name).first()
        reservation = Reservation.objects(user=user_id, product=product_id).first()
        form = ChangeStatusForm()
        if form.validate_on_submit():
            reservation.modify(status=form.status.data)
            reservation.save()
            return redirect(url_for("products.reservation_detail", product_name=product_name, user_name=user_name))
        return render_template("reservation_detail.html",reservation=reservation,user=user,product=product, form=form)
    else:
        return redirect(url_for("products.reservation"))
    


def plot_by_product():
    products = Product.objects()
    names = list(map(get_name, products))
    num_pending = list(map(get_num_pending, names))
    num_confirmed = list(map(get_num_confirmed, names))
    num_paid = list(map(get_num_paid, names))
    num_pickedup = list(map(get_num_pickedup, names))
    fig = go.Figure(data=[
        go.Bar(name='Pending', x=num_pending, y=names, orientation='h'),
        go.Bar(name='Confirned', x=num_confirmed, y=names, orientation='h'),
        go.Bar(name='Paid', x=num_paid, y=names, orientation='h'),
        go.Bar(name='Picked-Up', x=num_pickedup, y=names, orientation='h')
    ])
    fig.update_layout(barmode='stack')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def get_name(product):
    return product.get_name()
def get_num_pending(name):
    product_id = Product.objects(name=name).get()
    reservations = Reservation.objects(product=product_id,status=Status.PENDING.value)
    total = sum(list(map(get_amount, reservations)))
    return total
def get_num_confirmed(name):
    product_id = Product.objects(name=name).get()
    reservations = Reservation.objects(product=product_id,status=Status.CONFIRMED.value)
    total = sum(list(map(get_amount, reservations)))
    return total
def get_num_paid(name):
    product_id = Product.objects(name=name).get()
    reservations = Reservation.objects(product=product_id,status=Status.PAID.value)
    total = sum(list(map(get_amount, reservations)))
    return total
def get_num_pickedup(name):
    product_id = Product.objects(name=name).get()
    reservations = Reservation.objects(product=product_id,status=Status.PICKEDUP.value)
    total = sum(list(map(get_amount, reservations)))
    return total
def get_amount(reservation):
    return reservation.get_amount()

def plot_by_user():
    all_users = User.objects()
    good_users = []
    for user in all_users:
        reservations = Reservation.objects(user=user)
        # print(user.get_id())
        # print(reservations)
        if reservations:
            good_users.append(user.get_id())
    # print(good_users)
    nums = [3,3,2]
    # print(nums)
    fig = go.Figure([go.Bar(x=nums, y=good_users, orientation='h')])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON




