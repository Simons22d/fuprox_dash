from flask import render_template, url_for, flash, redirect, request, abort,jsonify
from fuprox import app, db,bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from fuprox.forms import (RegisterForm, LoginForm, BranchForm, CompanyForm, ServiceForm, SolutionForm,ReportForm)
from fuprox.models import User,Company,Branch, Service,Help,BranchSchema,CompanySchema,ServiceSchema,Mpesa, MpesaSchema,Booking,BookingSchema
from fuprox.utility import reverse


from datetime import datetime
import secrets
import socketio
from fuprox.utility import email
from flask_sqlalchemy import sqlalchemy

sio = socketio.Client()
socket_link = "http://127.0.0.1:5000/"


# rendering many route to the same template
branch_schema = BranchSchema()
service_schema = ServiceSchema()
services_schema = ServiceSchema(many=True)
company_schema =CompanySchema()
mpesa_schema = MpesaSchema()
mpesas_schema = MpesaSchema(many=True)
bookings_schema = BookingSchema(many=True)




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


@app.route("/doughnut/data",methods=["GET"])
def _doughnut_data():
    open_lookup = Booking.query.filter_by(serviced=False).all()
    open_data = bookings_schema.dump(open_lookup)
    closed_lookup = Booking.query.filter_by(serviced=True).all()
    closed_data = bookings_schema.dump(closed_lookup)

    return jsonify({"open":len(open_data),"closed":len(closed_data)})

@app.route("/bar/data",methods=["GET"])
def last_fifteen_data():
    data = get_issue_count()
    return jsonify(data["result"])




"""
function to get issue count >>>>
"""

def get_issue_count():
    data = db.session.execute("SELECT COUNT(*) AS issuesCount, DATE (date_added) AS issueDate FROM booking GROUP BY "
                           "issueDate LIMIT 15")
    return {'result': [dict(row) for row in data]}

"""
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::working with all forms of payments linking to the database::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
"""

@app.route("/payments")
@login_required
def payments():
    # work on the payments templates
    # get date from the database 
    lookup = Mpesa.query.all()
    data = mpesas_schema.dump(lookup)
    print("mpesa",data)
    return render_template("payment.html",transactions=data)


@app.route("/reverse",methods=["POST"])
def reverse_():
    """ PARAMS
    'Initiator' => 'testapi',
    'SecurityCredential' => 'eOvenyT2edoSzs5ATD0qQzLj/vVEIAZAIvIH8IdXWoab0NTP0b8xpqs64abjJmM8+cjtTOfcEsKfXUYTmsCKp5X3iToMc5xTMQv3qvM7nxtC/SXVk+aDyNEh3NJmy+Bymyr5ISzlGBV7lgC0JbYW1TWFoz9PIkdS4aQjyXnKA2ui46hzI3fevU4HYfvCCus/9Lhz4p3wiQtKJFjHW8rIRZGUeKSBFwUkILLNsn1HXTLq7cgdb28pQ4iu0EpVAWxH5m3URfEh4m8+gv1s6rP5B1RXn28U3ra59cvJgbqHZ7mFW1GRyNLHUlN/5r+Zco5ux6yAyzBk+dPjUjrbF187tg==',
    'CommandID' => 'TransactionReversal',
    'TransactionID' => 'NGE51H9MBP',
    'Amount' => '800',
    'ReceiverParty' => '600211',
    'RecieverIdentifierType' => '11',
    'ResultURL' => 'http://7ee727a4.ngrok.io/reversal/response.php',
    'QueueTimeOutURL' => 'http://7ee727a4.ngrok.io/reversal/response.php',
    'Remarks' => 'ACT_001',
    'Occasion' => 'Reverse_Cash'
    """
    id = request.json["id"]
    data = get_transaction(id)
    transaction_id = data["receipt_number"]
    amount = data["amount"]
    receiver_party = data["phone_number"]
    return reverse(transaction_id,amount,receiver_party)

def get_transaction(id): 
    lookup = Mpesa.query.get(id)
    return mpesa_schema.dump(lookup)



@app.route("/card")
@login_required
def payments_card():
    # get date from the database 
    lookup = Mpesa.query.all()
    data = mpesas_schema.dump(lookup)
    print("><>>>>>XX>>XXXXX")
    print("mpesa",data)
    # work on the payments templates
    return render_template("payment_card.html", transactions=data)


@app.route("/reports")
@login_required
def payments_report():
    # work on the payments templates
    return render_template("payments_reports.html")

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
        this_company_data = Company.query.filter_by(name=branch.company.data).first()
        if this_company_data :
            key_ = secrets.token_hex();
            data = Branch(branch.name.data, branch.company.data, branch.longitude.data, branch.latitude.data,
                          branch.opens.data,
                          branch.closes.data, branch.service.data, branch.email.data,key_)
            if not branch_exits(branch.name.data):
                data_ = branch_schema.dump(data)
                # here we are going to push  the branch data to the lacalhost
                sio.emit("branch", data_)
                # we are going to email the sender
                db.session.add(data)
                db.session.commit()
                # we are going to email.
                body = f"""
                                 <div marginheight="0" marginwidth="0" style="background:#fafafa;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;min-width:100%;padding:0;text-align:left;width:100%!important" bgcolor="#fafafa">
                                 <table style="background:#fafafa;border-collapse:collapse;border-spacing:0;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;height:100%;line-height:19px;margin:0;padding:10px;text-align:left;vertical-align:top;width:100%" bgcolor="#fafafa">
                                   <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                     <td align="center" valign="top" style="border-collapse:collapse!important;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:center;vertical-align:top;word-break:break-word">
                                       <center style="min-width:580px;width:100%">

                                         <table style="border-collapse:collapse;border-spacing:0;margin:0 auto;padding:0;text-align:inherit;vertical-align:top;width:580px">
                                           <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                             <td style="border-collapse:collapse!important;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:left;vertical-align:top;word-break:break-word" align="left" valign="top">

                                               <table style="border-collapse:collapse;border-spacing:0;margin-top:20px;padding:0;text-align:left;vertical-align:top;width:100%">
                                                 <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                                   <td align="center" style="border-collapse:collapse!important;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:center;vertical-align:top;word-break:break-word" valign="top">
                                                     <center style="min-width:580px;width:100%">
                                                       <div style="margin-bottom:30px;margin-top:20px;text-align:center!important" align="center !important">
                             <!--                            <img src="https://drive.google.com/file/d/15a4HIX5Lhgwydm03V_GFVMkUT-vsBJRF/view?usp=sharing" width="50" height="48" style="clear:both;display:block;float:none;height:48px;margin:0 auto;max-height:48px;max-width:50px;outline:none;text-decoration:none;width:50px" align="none" class="CToWUd">-->
                                                       </div>
                                                     </center>
                                                   </td>
                                                   <td style="border-collapse:collapse!important;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:left;vertical-align:top;width:0px;word-break:break-word" align="left" valign="top"></td>
                                                 </tr>
                                               </tbody></table>

                                               <table style="background:#ffffff;border-collapse:collapse;border-radius:3px!important;border-spacing:0;border:1px solid #dddddd;padding:0;text-align:left;vertical-align:top" bgcolor="#ffffff">
                                                 <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                                   <td style="border-collapse:collapse!important;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:left;vertical-align:top;word-break:break-word" align="left" valign="top">

                                                     <div style="color:#333333;font-size:14px;font-weight:normal;line-height:20px;margin:20px">
                             <table style="background:#fff;border-collapse:separate!important;border-spacing:0;box-sizing:border-box;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;height:100%;line-height:19px;margin:0;padding:10px;text-align:left;vertical-align:top;width:100%" width="100%" bgcolor="#fff">
                                 <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                     <td style="border-collapse:collapse!important;box-sizing:border-box;color:#222222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:left;vertical-align:top;word-break:break-word" valign="top" align="left"></td>
                                     <td style="border-collapse:collapse!important;box-sizing:border-box;color:#222222;display:block;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:14px;font-weight:normal;line-height:19px;margin:0 auto;max-width:580px;padding:24px;text-align:left;vertical-align:top;width:580px;word-break:break-word" width="580" valign="top" align="left">
                                         <div style="box-sizing:border-box;display:block;margin:0 auto;max-width:580px">


                             <table cellpadding="0" cellspacing="0" style="border-collapse:separate!important;border-spacing:0;box-sizing:border-box;margin:0 0 30px;padding:0;text-align:left;vertical-align:top;width:100%" width="100%">
                               <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                 <td align="" style="border-collapse:collapse!important;box-sizing:border-box;color:#222222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:left;vertical-align:top;word-break:break-word" valign="top">
                                   <table cellpadding="0" cellspacing="0" style="border-collapse:separate!important;border-spacing:0;box-sizing:border-box;padding:0;text-align:left;vertical-align:top;width:auto">
                                     <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                       <td style="background:#0366d6;border-collapse:collapse!important;border-radius:5px;box-sizing:border-box;color:#222222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:center;vertical-align:top;word-break:break-word" valign="top" bgcolor="#0366d6" align="center">
                                       </td>
                                     </tr>
                                   </tbody></table>
                                 </td>
                               </tr>
                             </tbody></table>

                             <p style="color:#222222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:14px;font-weight:normal;line-height:1.5;margin:0 0 15px;padding:0;text-align:left" align="left">
                                  Dear Sir/Madam, <br><br>
                                                 Please find the key below, this key is required forthe applications to
                                                 work for the branch <b> {branch.name.data}. </b>
                                                 <br>Please do not loose this key.
                                                 <br><br>
                                                 <pre></pre>
                                                 <br>
                                                 If your are not sure of how to use the key on the applications. <br><br>
                                                 Please Follow <a href='http://68.183.89.127:3000/help'>this</a>
                                                 link to get more infomation and other documents.<br><br>

                                                 Kind Regards,<br>
                                                 IT Support.<br><br><br>

                             </p>
                             <p
                                     style="color:#586069!important;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:12px!important;font-weight:normal;line-height:1.5;margin:0 0 15px;padding:0;text-align:left" align="left">You are receiving this email because a branch was added with your email on our platform.</p>


                                             <div style="box-sizing:border-box;clear:both;width:100%">
                                                 <hr style="background:#d9d9d9;border-style:solid none none;border-top-color:#e1e4e8;border-width:1px 0 0;color:#959da5;font-size:12px;height:0;line-height:18px;margin:24px 0 30px;overflow:visible">
                                           <div style="box-sizing:border-box;color:#959da5;font-size:12px;line-height:18px">
                                             <p style="color:#959da5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:12px;font-weight:normal;line-height:18px;margin:0 0 15px;padding:0;text-align:center" align="center">
                                                     </p>
                                           </div>
                                             </div>
                                         </div>

                                     </td>
                                     <td style="border-collapse:collapse!important;box-sizing:border-box;color:#222222;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:left;vertical-align:top;word-break:break-word" valign="top" align="left"></td>
                                 </tr>
                             </tbody></table>





                                                     </div>

                                                   </td>
                                                 </tr>
                                               </tbody></table>

                                               <table style="border-collapse:collapse;border-spacing:0;margin-bottom:30px;padding:0;text-align:left;vertical-align:top;width:100%">
                                                 <tbody><tr style="padding:0;text-align:left;vertical-align:top" align="left">
                                                   <td align="center" style="border-collapse:collapse!important;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:center;vertical-align:top;word-break:break-word" valign="top">
                                                   </td>
                                                   <td style="border-collapse:collapse!important;color:#222222;font-family:'Helvetica','Arial',sans-serif;font-size:14px;font-weight:normal;line-height:19px;margin:0;padding:0;text-align:left;vertical-align:top;width:0px;word-break:break-word" align="left" valign="top"></td>
                                                 </tr>
                                               </tbody></table>

                                             </td>
                                           </tr>
                                         </tbody></table>

                                       </center>
                                     </td>
                                   </tr>
                                 </tbody></table><div class="yj6qo"></div><div class="adL">

                               </div></div><div class="adL">

                             """
                try:
                    try:
                        pass
                    except socket.gaierror:
                        pass
                    # email((branch.email.data).strip(),"Branch Key from Fuprox",body)
                    pass
                except UnicodeEncodeError :
                    # warn about sending a email and offer a link to sending the email
                    print("Error! error Sending email")
                branch.name.data = ""
                branch.company.data = ""
                branch.longitude.data = ""
                branch.latitude.data = ""
                branch.opens.data = ""
                branch.closes.data = ""
                branch.service.data = ""
                branch.email.data = ""
                flash(f"Branch Successfully Added", "success")
            else :
                flash("branch by that name exists","warning")
                redirect(url_for("home"))
        else:
            flash("Company Does Not exist. Add company name first.","danger")
    return render_template("add_branch.html",form=branch,companies = company_data,services=service_data)


""" not recommemded __check if current branhc is in db"""
def branch_exits(name):
    lookup = Branch.query.filter_by(name=name).first()
    branch_data = branch_schema.dump(lookup)
    return branch_data


# mpesa more info
@app.route("/info/<string:key>")
def more_info(key):
    print("key",key)
    lookup = Mpesa.query.get(key)
    data = mpesa_schema.dump(lookup)
    return render_template("info.html",data=data)


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
        # medical
        if company.is_medical.data == "True":
            final = True
        else :
            final = False
        try:
            data = Service(company.name.data, company.service.data,final)
            db.session.add(data)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash(f"Category By That Name Exists","warning")
        # adding a category
        sio.emit("category",  service_schema.dump(data))
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

            try:
                data = Company(company.name.data, company.service.data)
                db.session.add(data)
                db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                flash("Company By That Name Exists","warning")
            # add company
            sio.emit("company", company_schema.dump(data))

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
        try:
            user = User(username=register.username.data, email=register.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash("User By That Username Exists","warning")
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
        try:
            user = User(username=register.username.data, email=register.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash("User By That Name Exists","warning")
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
        try:
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
        except sqlalchemy.exc.IntegrityError:
            flash("Branch By That Name Exists","warning")

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
        flash("Company Does Not exist. Add company name first.", "danger")
            
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
        flash("Company Does Not exist. Add company name first.", "danger")
            
    return render_template("edit_company.html", form=company, services=services)



@app.route("/email",methods=["POST"])
def send_email():
    to = request.json["email"]
    subject = request.json["subject"]
    body = request.json["body"]
    return email(to,subject,body)

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


# TODO : app Issues

