from flask import render_template, url_for, flash, redirect, request, abort
from fuprox import app, db, ma,bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from fuprox.forms import (RegisterForm, LoginForm, ResetRequest, ResetPassword, BranchForm,
                          OrganizationForm,ServiceForm)
from fuprox.models import User,Company,Branch,UserSchema,CompanySchema,BranchSchema, Service, ServiceSchema
import json
import jsonify

user_schema = UserSchema()
# rendering many route to the same template
@app.route("/")
@app.route("/dashboard")
def home():
    # rendering template
    return render_template("branches.html")


@app.route("/payments")
def payments():
    return render_template("payment.html")





@app.route("/branches")
@app.route("/branches/add",methods=["POST","GET"])
def branches():
    # init the form
    branch = BranchForm()
    if branch.validate_on_submit():
        data = Branch(branch.name.data,branch.company.data,branch.longitude.data,branch.latitude.data,branch.opens.data,
                      branch.closes.data,branch.service.data,branch.description.data)
        db.session.add(data)
        db.session.commit()
        branch.name.data = ""
        branch.company.data = ""
        branch.longitude.data = ""
        branch.latitude.data = ""
        branch.opens.data = ""
        branch.closes.data = ""
        branch.service.data = ""
        branch.description.data = ""

        flash(f"Branch Successfully Added", "success")
    return render_template("add_branch.html",form=branch)

#view_branch
@app.route("/branches/view")
def view_branch():
    company = ServiceForm()
    return render_template("view_branch.html",form=company)

@app.route("/branches/category")
@app.route("/branches/category/add",methods=["POST","GET"])
def add_category():
    company = ServiceForm()
    if company.validate_on_submit():
        data = Service(company.name.data, company.service.data)
        db.session.add(data)
        db.session.commit()
        company.name.data = ""
        company.service.data = ""
        flash(f"Company Successfully Added", "success")
    return render_template("add_category.html",form=company)


@app.route("/branches/company",methods=["GET","POST"])
@app.route("/branches/company/add",methods=["POST","GET"])
def add_company():
    # init the form
    company = OrganizationForm()
    if company.validate_on_submit():
        data = Company(company.name.data,company.service.data)
        db.session.add(data)
        db.session.commit()
        company.name.data = ""
        company.service.data = ""
        flash(f"Company Successfully Added", "success")
    return render_template("add_company.html",form=company)


@app.route("/branches/company/view")
def view_company():
    # init the form
    branch = BranchForm()
    return render_template("view_company.html", form=branch)


@app.route("/branches/category/view")
def view_category():
    # init the form
    branch = BranchForm()
    return render_template("view_category.html", form=branch)


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/extras")
def extras():
    return render_template("extras.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/login",methods=["POST","GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    login = LoginForm()
    if login.validate_on_submit():
        name = "denis"
        user = User.query.filter_by(email=login.email.data).first()
        user_data = user_schema.dump(user)
        if name:
            next_page = request.args.get("next")
            # login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login unsuccessful Please Check Email and Password", "danger ")
    return render_template("login.html", form=login)


@app.route("/register", methods=["GET", "POST"])
def register():
    # checking if the current user is logged
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    register = RegisterForm()
    if register.validate_on_submit():
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(register.password.data).decode("utf-8")
        # adding the password to the database
        user = User(username=register.username.data, email=register.email.data, password=hashed_password,image_file="")
        db.session.add(user)
        db.session.commit()

        flash(f"Account Created successfully", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=register)