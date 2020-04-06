from flask import render_template, url_for, flash, redirect, request, abort
from fuprox import app, db,bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from fuprox.forms import (RegisterForm, LoginForm, BranchForm, CompanyForm, ServiceForm, SolutionForm,ReportForm)
from fuprox.models import User,Company,Branch, Service,Help,BranchSchema
from datetime import datetime
import secrets
import socketio

sio = socketio.Client()
socket_link = "http://127.0.0.1:5000/"


# rendering many route to the same template
branch_schema = BranchSchema()

@app.route("/")
@app.route("/dashboard")
@login_required
def home():
    # date
    date = datetime.now().strftime("%A, %d %B %Y")
    # report form
    # report = ReportForm()
    # rendering template
    return render_template("dashboard.html",today=date)


@app.route("/payments")
@login_required
def payments():
    # work on the payments templates
    return render_template("payment.html")


@app.route("/branches")
@app.route("/branches/add",methods=["POST","GET"])
@login_required
def branches():
    # get data from the database
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

            # here we are going to push  the branch data to the lacalhost
            sio.emit("branch",branch_schema.dump(data))

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
        final = bool()
        if company.is_medical.data == "True":
            final = True
        else :
            final = False
        data = Service(company.name.data, company.service.data,final)
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
    company = CompanyForm()
    if company.validate_on_submit():
        # getting if the company type exists within the service types
        service_type  = Service.query.get(int(company.service.data))
        if service_type :
            data = Company(company.name.data, company.service.data)
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


# new ]

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
    branch_data = Branch.query.get(id)
    # setting form inputs to the data in the database

    service_data = Service.query.all()
    # init the form
    branch = BranchForm()
    if branch.validate_on_submit():
        # update data in the database 
        branch_data.name = branch.name.data
        branch_data.longitude = branch.longitude.data
        branch_data.latitude = branch.latitude.data
        branch_data.service = branch.service.data
        branch_data.opens = branch.opens.data
        branch_data.closes = branch.closes.data
        branch_data.company = branch.company.data
        branch_data.description = branch.description.data
        
        # update date to the database
        db.session.commit()

        # here we are going to push  the branch data to the lacalhost
        sio.emit("branch_edit", branch_schema.dump(branch_data))

        # prefilling the form with the empty fields
        branch.name.data = ""
        branch.company.data = ""
        branch.longitude.data = ""
        branch.latitude.data = ""
        branch.opens.data = ""
        branch.closes.data = ""
        branch.service.data = ""
        branch.description.data = ""
        flash("Branch Successfully Updated", "success")
        return redirect(url_for("view_branch"))
    elif request.method == "GET":
        branch.name.data = branch_data.name
        branch.longitude.data = branch_data.longitude
        branch.latitude.data = branch_data.latitude
        branch.service.data = branch_data.service
        branch.opens.data = branch_data.opens
        branch.closes.data = branch_data.closes
        branch.company.data = branch_data.company
        branch.description.data = branch_data.description

    else:
        flash("Company Does Not exist. Add copmany name first.", "danger")
            
    return render_template("edit_branch.html", form=branch, companies=company_data, services=service_data)


@app.route("/branch/delete/<int:id>",methods=["GET","POST"])
@login_required
def delete_branch(id):
    # get the branch data
    branch_data = Branch.query.get(id)
    db.session.delete(branch_data)
    db.session.commit()
    flash("Branch Deleted Sucessfully","success")
    # init the form
    branch = BranchForm()
    return render_template("delete_branch.html", form=branch, data=branch_data)


# edit company
@app.route("/company/edit/<int:id>",methods=["GET","POST"])
@login_required
def edit_company(id):
    this_company = Company.query.get(id)
    # setting form inputs to the data in the database
    services = Service.query.all()
    # # init the form
    company = CompanyForm()
    if company.validate_on_submit():
        # update data in the database 
        this_company.name = company.name.data
        this_company.service = company.service.data
        
        # update date to the database
        db.session.commit()

        # prefilling the form with the empty fields
        company.name.data = ""
        company.service.data = ""
    
        flash("Company Successfully Updated", "success")

        return redirect(url_for("view_company"))
    elif request.method == "GET":
        company.name.data = this_company.name
        company.service.data = this_company.service
        

    else:
        flash("Company Does Not exist. Add copmany name first.", "danger")
            
    return render_template("edit_company.html", form=company, services=services)



# edit company
@app.route("/category/edit/<int:id>",methods=["GET","POST"])
@login_required
def edit_category(id):
    this_category = Service.query.get(id)
    # setting form inputs to the data in the database
    # # init the form
    service = ServiceForm()
    if service.validate_on_submit():
        # update data in the database 
        this_category.name = service.name.data
        this_category.service = service.service.data
        
        # update date to the database
        db.session.commit()

        # prefilling the form with the empty fields
        service.name.data = ""
        service.service.data = ""
    
        flash("Company Successfully Updated", "success")
        return redirect(url_for("view_category"))

    elif request.method == "GET":
        service.name.data = this_category.name
        service.service.data = this_category.service
    else:
        flash("Company Does Not exist. Add company name first.", "danger")
    return render_template("edit_category.html", form=service)

'''working with sockets '''
try:
    sio.connect(socket_link)
except socketio.exceptions.ConnectionError:
    print("Error! Could not connect to the socket server.")
    # print("...")
