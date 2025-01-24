from flask import Flask, render_template, request, session, redirect, url_for, flash
from dbmodel import *
import json
import os
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'super-secret-key'
with open('config.json', 'r') as c:
    params = json.load(c)["params"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db.init_app(app)
app.app_context().push()
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}



@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('cname')
        userpass = request.form.get('cpass')

        # Query the database for the user
        customer = Customer.query.filter_by(cname=username, password=userpass).first()

        if customer:
            # If user exists, store their info in the session and redirect
            session['user'] = customer.cname
            return redirect('/cview')
        else:
            # If login fails, show an error message
            error = "Invalid username or password. Please try again."
            return render_template('login.html', params=params, error=error)

    # Render login page for GET requests
    return render_template('login.html', params=params)

@app.route("/signup",methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username = request.form.get('cname')
        userpass = request.form.get('cpass')
        c=Customer(cname=username,password=userpass)
        db.session.add(c)
        db.session.commit()
        return redirect('/login')
    return render_template('/signup.html')

@app.route("/alogin",methods=['GET','POST'])
def alogin():
    


    if request.method=='POST':
        username = request.form.get('aname')
        userpass = request.form.get('apass')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            session['admin'] = username
            return redirect("/aview")
    return render_template('/alogin.html',params=params)

@app.route("/plogin",methods=['GET','POST'])
def plogin():
    if request.method == 'POST':
        username = request.form.get('pname')
        userpass = request.form.get('ppass')

        # Query the database for the user
        p = Partner.query.filter_by(name=username, password=userpass).first()

        if p:
            # If partner exists, store their info in the session and redirect
            session['partner'] = p.name
            return redirect('/pview')
        else:
            # If login fails, show an error message
            error = "Invalid username or password. Please try again."
            return render_template('plogin.html', params=params, error=error)

    # Render login page for GET requests
    return render_template('plogin.html', params=params)

@app.route("/psignup",methods=['GET','POST'])
def psignup():
    if request.method=='POST':
        partname = request.form.get('name')
        partpass = request.form.get('ppass')
        partdesc = request.form.get('sdesc')
        partserv = request.form.get('sname')
        sdate=datetime.now()
        p=Partner(name=partname,password=partpass,desc=partdesc,sname=partserv,date_of_join=sdate)
        db.session.add(p)
        db.session.commit()
        return redirect('/plogin')
    services=Service.query.all()
    return render_template('/psignup.html',services=services)

@app.route("/cview", methods=['GET', 'POST'])
def cview():
    # Ensure the user is logged in
    if 'user' not in session:
        return redirect('/login')
    
    approved_partners = Partner.query.filter_by(approved=True).all()
    services = Service.query.all()
    
    if request.method == 'POST':
        # Get form data
        partner_name = request.form.get('partner')
        
        date_of_request = datetime.now()
        customer_name = session['user']
        
        # Get the IDs for the selected service and partner
        
        selected_partner = Partner.query.filter_by(name=partner_name).first()
        customer = Customer.query.filter_by(cname=customer_name).first()

        # Ensure entities exist
        if selected_partner and customer:
            new_request = ServiceRequest(
                service_id=selected_partner.sname,
                customer_id=customer.cname,
                partner_id=selected_partner.name,
                date_of_request=date_of_request,
                service_status='requested'
            )
            db.session.add(new_request)
            db.session.commit()
            flash("Service request submitted successfully!", "success")
        else:
            flash("Invalid service request. Please check your inputs.", "error")

    return render_template(
        'cview.html',
        username=session['user'],
        partners=approved_partners,
        services=services
    )


@app.route("/aview",methods=['GET','POST'])
def aview():
    if 'admin' not in session:
        return redirect('/alogin')
    return render_template('/aview.html')


@app.route("/pcheck",methods=['GET','POST'])
def pcheck():
    if 'admin' not in session:
        return redirect('/alogin')

    all_partners=Partner.query.all()
    return render_template('/pcheck.html',all_partners=all_partners)

@app.route("/pcheck/verified",methods=['GET','POST'])
def verifiedpcheck():
    if 'admin' not in session:
        return redirect('/alogin')
        
    all_partners=Partner.query.filter_by(approved=True).all()
    return render_template('/pcheck.html',all_partners=all_partners)

@app.route("/pcheck/unverified",methods=['GET','POST'])
def unverifiedpcheck():
    if 'admin' not in session:
        return redirect('/alogin')
        
    all_partners=Partner.query.filter_by(approved=False).all()
    return render_template('/pcheck.html',all_partners=all_partners)

# @app.route("/pcheck/<string:name>",methods=['GET','POST'])
# def partnerdetails(name):
#     if 'admin' not in session:
#         return redirect('/alogin')
    
#     partner=Partner.query.filter_by(name=name).first()
#     if not partner:
#         return "Partner Not Found"
#     return render_template('/pcheck.html',all_partners=partner)
    
@app.route("/approve_partner", methods=['POST'])
def approve_partner():
    if 'admin' not in session:
        return redirect('/alogin')

    # Get partner ID from the form
    partner_id = request.form.get('partner_id')

    # Query the partner from the database
    partner = Partner.query.get(partner_id)

    if not partner:
        return "Partner Not Found", 404

    # Update the 'approved' status
    partner.approved = True

    # Commit the changes to the database
    db.session.commit()

    # Redirect back to the pcheck page
    return redirect("/pcheck")

@app.route("/services",methods=['GET','POST'])
def services():
    if 'admin' not in session:
        return redirect('/alogin')

    services=Service.query.all()
    
    return render_template('/services.html',services=services) 

@app.route("/addservices",methods=['GET','POST'])
def addservices():
    if 'admin' not in session:
        return redirect('/alogin')
    if request.method=='POST':
        sname = request.form.get('name')
        sprice = request.form.get('price')
        sdesc = request.form.get('sdesc')
        s=Service(name=sname,desc=sdesc,price=sprice)
        db.session.add(s)
        db.session.commit()
        return render_template('/services.html')    
    
    return render_template('/addservices.html') 

@app.route("/pview", methods=['GET', 'POST'])
def pview():
    if 'partner' not in session:
        return redirect('/plogin')
    
    # Get all requested service requests assigned to the logged-in partner
    partner_name = session['partner']
    partner_requests = ServiceRequest.query.filter_by(partner_id=partner_name).all()
    
    if request.method == 'POST':
        # Handle status change
        request_id = request.form.get('request_id')
        new_status = request.form.get('status')
        
        # Fetch the service request by ID
        service_request = ServiceRequest.query.filter_by(id=request_id,partner_id=partner_name).first()
        
        if service_request:
            service_request.service_status = new_status
            db.session.commit()
            flash("Service request status updated successfully!", "success")
        else:
            flash("Invalid service request ID.", "error")
    
    return render_template('/pview.html', requests=partner_requests)




if __name__=="__main__":
    app.run(debug='true')