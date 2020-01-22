from flask import render_template, url_for, flash, redirect, request, abort
from fuprox import app, db, ma,bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from fuprox.forms import (RegisterForm, LoginForm, ResetRequest, ResetPassword, BranchForm,
                          OrganizationForm,ServiceForm,SolutionForm,SearchForm)

from fuprox.models import User,Company,Branch, Service,Help
import json
import jsonify

# rendering many route to the same template

@app.route("/")
@app.route("/dashboard")
@login_required
def home():
    # rendering template
    return render_template("branches.html")


@app.route("/payments")
@login_required
def payments():
    # work on the payments templates
    return render_template("payment.html")


@app.route("/branches")
@app.route("/branches/add",methods=["POST","GET"])
@login_required
def branches():# get data from the database
    company_data = Company.query.all()
    service_data = Service.query.all()
    # init the form
    branch = BranchForm()
    if branch.validate_on_submit():
        # get specific compan data
        this_company_data = Company.query.get(branch.company.data)
        if this_company_data :
            data = Branch(branch.name.data, branch.company.data, branch.longitude.data, branch.latitude.data,
                          branch.opens.data,
                          branch.closes.data, branch.service.data, branch.description.data)
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
        else:
            flash("Company Does Not exist. Add copmany name first.","danger")

    return render_template("add_branch.html",form=branch,companies = company_data,services=service_data)

# view_branch


@app.route("/branches/view")
@login_required
def view_branch():
    # get data from the database
    branches_data = Branch.query.all()
    company = ServiceForm()
    return render_template("view_branch.html",form=company,data = branches_data)



@app.route("/branches/category")
@app.route("/branches/category/add",methods=["POST","GET"])
@login_required
def add_category():
    company = ServiceForm()
    # checkinf the mentioed  comapany exists
    if company.validate_on_submit():
        data = Service(company.name.data, company.service.data)
        db.session.add(data)
        db.session.commit()
        company.name.data = ""
        company.service.data = ""
        flash(f"Service Successfully Added", "success")
    return render_template("add_category.html", form=company)



@app.route("/branches/company", methods=["GET", "POST"])
@app.route("/branches/company/add", methods=["POST", "GET"])
@login_required
def add_company():
    service_data = Service.query.all()
    # init the form
    company = OrganizationForm()
    if company.validate_on_submit():
        # getting if the company type exists within the service types
        service_type  = Service.query.get(int(company.service.data))
        if service_type :
            data = Company(company.name.data, company.service.data)
            print(company.name.data, company.service.data)
            db.session.add(data)
            db.session.commit()
            company.name.data = ""
            company.service.data = ""
            flash(f"Company Successfully Added", "success")
        else :
            flash("Service type Provided does not exist. Please add it first.","error")
    return render_template("add_company.html", form=company ,companies = service_data)


@app.route("/branches/company/view")
@login_required
def view_company():
    # get the branch data
    company_data = Company.query.all()
    # init the form
    branch = BranchForm()
    return render_template("view_company.html", form=branch, data =company_data)


@app.route("/branches/category/view")
@login_required
def view_category():
    # category data
    service_data = Service.query.all()
    # init the form
    branch = BranchForm()
    return render_template("view_category.html", form=branch, data=service_data)


@app.route("/help",methods=["GET","POST"])
@login_required
def help():
    # init form
    # search_form = SearchForm()
    # if(search_form.validate_on_submit()):
    #     # make a query to the database
    #     data = Help.query.filter_by(solution=search_form.term.data).all()
    #     # Model.query.filter(Model.columnName.contains('sub_string'))
    #     redirect("search_result.html",200,data=data)
    # get data from the solutions page
    solution_data = Help.query.all()
    return render_template("help.html",data = solution_data)


@app.route("/extras")
@login_required
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

    #loading the form
    login = LoginForm()

    #checking the form data status
    if login.validate_on_submit():
        print("form_data",login.email.data,login.password.data)
        user = User.query.filter_by(email=login.email.data).first()
        print("user_data",user)
        if user and bcrypt.check_password_hash(user.password, login.password.data):
            next_page = request.args.get("next")
            login_user(user)
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login unsuccessful Please Check Email and Password", "danger ")
    return render_template("login.html", form=login)


@app.route("/register", methods=["GET", "POST"])
# @login_required
def register():
    # checking if the current user is logged
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    register = RegisterForm()
    if register.validate_on_submit():
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(register.password.data).decode("utf-8")
        # adding the password to the database
        user = User(username=register.username.data, email=register.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f"Account Created successfully", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=register)


# new routes

@app.route("/extras/desktop")
@login_required
def desktop_app():
    pass


@app.route("/extras/mobile")
@login_required
def mobile_app():
    pass


''' working with users'''
@app.route("/extras/users/add",methods=["GET","POST"])
@login_required
def add_users():
    # getting user data from the database
    user_data = User.query.all()

    # return form to add a user
    register = RegisterForm()

    if register.validate_on_submit():
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(register.password.data).decode("utf-8")
        # adding the password to the database
        user = User(username=register.username.data, email=register.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f"Account Created successfully", "success")

    return render_template("add_users.html", form=register,data=user_data)


@app.route("/extras/users/view")
@login_required
def view_users():
    pass


@app.route("/extras/users/manage")
@login_required
def manage_users():
    pass


# SEARCHING ROUTE
@app.route("/help/solution/<int:id>",methods=["GET","POST"])
@login_required
def search(id):
    # get data from the database based on the data provided
    data = Help.query.get(id)
    # there should be a solution database || FAQ
    return render_template("search.html",data=data)


@app.route("/help/solution/add",methods=["GET","POST"])
@login_required
def add_solution():
    solution_form = SolutionForm()
    if solution_form.validate_on_submit():

        topic = solution_form.topic.data
        title = solution_form.title.data
        sol = solution_form.solution.data

        solution_data = Help(topic,title,sol)
        db.session.add(solution_data)
        db.session.commit()
        flash("Solution Added Successfully","success")

        # render a html && add the data to the page
    return render_template("add_solution.html",form=solution_form)




# the edit routes
@app.route("/branch/edit/<int:id>",methods=["GET","POST"])
@login_required
def edit_branch(id):
    company_data = Company.query.all()
    data = Branch.query.get(id)
    # setting form inputs to the data in the database

    service_data = Service.query.all()
    # init the form
    branch = BranchForm()
    branch.name.data = data.name
    branch.longitude.data = data.longitude
    branch.latitude.data = data.latitude
    branch.service.data = data.service
    branch.opens.data = data.opens
    branch.closes.data = data.closes
    branch.company.data = data.company
    branch.description.data = data.description
    if branch.validate_on_submit():
        # get specific compan data
        this_company_data = Company.query.get(branch.company.data)
        if this_company_data:
            # update data in the database 
            data.name = branch.name.data
            data.longitude = branch.longitude.data
            data.latitude = branch.latitude.data
            data.service = branch.service.data
            data.opens = branch.opens.data
            data.closes = branch.closes.data
            data.company = branch.company.data
            data.description = branch.description.data
            
            # update date to the database
            db.session.commit()

            # prefilling the form with the empty fields
            branch.name.data = ""
            branch.company.data = ""
            branch.longitude.data = ""
            branch.latitude.data = ""
            branch.opens.data = ""
            branch.closes.data = ""
            branch.service.data = ""
            branch.description.data = ""
            flash(f"Branch Successfully Updated", "success")
            redirect(url_for("view_branch"))
        else:
            flash("Company Does Not exist. Add copmany name first.", "danger")

    return render_template("edit_branch.html", form=branch, companies=company_data, services=service_data)


@app.route("/branch/delete/<int:id>",methods=["GET","POST"])
@login_required
def delete_branch(id):
    # get the branch data
    branch_data = Branch.query.all()
    # init the form
    branch = BranchForm()
    return render_template("delete_branch.html", form=branch, data=branch_data)
