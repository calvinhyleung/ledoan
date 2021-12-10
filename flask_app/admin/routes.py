from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user



admin = Blueprint("admin", __name__)

@admin.route("/admin", methods=["GET", "POST"])
def notlogin():
    
    return render_template("admin_login.html")
