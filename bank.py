from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:3306/Bank_Loan'
app.config['UPLOAD_FOLDER'] = 'static'
app.config['SECRET_KEY'] = '5rt6y7uigvbhjbhvftfcgh'
db = SQLAlchemy(app)

# Table creation

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    phn_no = db.Column(db.String(20), unique=True)
    email_id = db.Column(db.String(200))
    password = db.Column(db.String(200))
    loans = db.relationship('Loan', back_populates='user', cascade='all, delete-orphan')

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    adhaar_id = db.Column(db.Integer)
    bank_name = db.Column(db.String(100))
    acc_no = db.Column(db.String(20))
    loan_apply_date = db.Column(db.Date)
    loan_amount = db.Column(db.Integer)
    tenure = db.Column(db.Integer)
    status = db.Column(db.String(50))
    user = db.relationship('Users', back_populates='loans')

class EMI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    monthly_emi_amt = db.Column(db.Integer)
    bal_amt = db.Column(db.Integer)
    payment_date = db.Column(db.Date)
    late_fee = db.Column(db.Integer)
    current_bal = db.Column(db.Integer)
    total_paid_amt = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False) 

# user post method
    
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    name = data.get("name")
    dob = data.get("dob")
    gender = data.get("gender")
    phn_no = data.get("phn_no")
    email_id = data.get("email_id")
    password = data.get("password")

    if dob is not None:
        dob = datetime.strptime(dob, '%Y-%m-%d').date()

    new_user = Users(name=name, dob=dob, gender=gender, phn_no=phn_no, email_id=email_id, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'user added successfully'})

# getalluser method

@app.route('/getalluser', methods=['GET'])
def getAlluserid():
        all_user = Users.query.all()
        userid_list = []
        for i in all_user:
           userid_list.append({
                'name': i.name,
                'dob' : i.dob,
                'gender' : i.gender,
                'phn_no': i.phn_no,
                'email_id': i.email_id,
                "password" : i.password
            })
        return jsonify({'data': userid_list})

# user getbyid method

@app.route('/getbyuserid/<int:id>', methods=['GET'])
def getByuserId(id):
        allid = Users.query.filter_by(id=id).first()
        
        return jsonify({
                'name':  allid.name,
                'dob' : allid.dob,
                'gender' : allid.gender,
                'phn_no':  allid.phn_no,
                'email_id':  allid.email_id,
                'password': allid.password 
            })

# user Update method

@app.route('/update_user/<int:id>', methods=['PUT'])
def updateuser(id):
        data = request.get_json()
        userupdate = Users.query.get(id)
        userupdate .name = data.get('name', userupdate .name)  
        userupdate .dob = data.get('dob', userupdate .dob)
        userupdate .gender = data.get('gender', userupdate .gender)
        userupdate .phn_no = data.get('phn_no', userupdate .phn_no)
        userupdate .email_id = data.get('email_id', userupdate .email_id)
        userupdate .password = data.get('password', userupdate .password)
        db.session.commit()
        return jsonify({'message': 'user successfully updated'})

# loan post method

@app.route('/add_loan', methods=['POST'])
def add_loan():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        adhaar_id = data.get("adhaar_id")
        bank_name = data.get("bank_name")
        acc_no = data.get("acc_no")
        loan_apply_date = datetime.strptime(data.get("loan_apply_date"), "%Y-%m-%d")
        loan_amount = data.get("loan_amount")
        tenure_end_date = data.get("tenure_end_date")
        status = data.get("status")

        new_loan = Loan(
            user_id=user_id, adhaar_id=adhaar_id, bank_name=bank_name, acc_no=acc_no,
            loan_apply_date=loan_apply_date, loan_amount=loan_amount,
            tenure=tenure_end_date, status=status
        )
        db.session.add(new_loan)
        db.session.commit()

        if status == "completed":
            emi_amt = loan_amount / tenure_end_date
            for i in range(1, tenure_end_date + 1):
                payment_date = loan_apply_date + timedelta(days=30 * i)
                emi = EMI(
                    loan_id=new_loan.id,
                    monthly_emi_amt=emi_amt,
                    payment_date=payment_date
                )
                db.session.add(emi)

            db.session.commit()

        return jsonify({"message": "Loan added successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# emi post method
    
@app.route('/add_emi', methods=['POST'])
def add_emi():
    try:
        data = request.get_json()
        loan_id = data.get("loan_id")
        payment_date = datetime.strptime(data.get("payment_date"), "%Y-%m-%d")

        loan = Loan.query.get(loan_id)
        emi_amt = loan.loan_amount / loan.tenure

        new_emi = EMI(
            loan_id=loan_id,
            monthly_emi_amt=emi_amt,
            payment_date=payment_date,
            bal_amt=0,
            total_paid_amt=0,
            late_fee=0,
            current_bal=0,
            completed=False
        )

        db.session.add(new_emi)
        db.session.commit()

        return jsonify({"message": "EMI added successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)})
    
#  emi update method

@app.route('/update_emi/<int:id>', methods=['PUT'])
def update_emi(id):
    emi = EMI.query.get(id)
    emi_amt = emi.monthly_emi_amt

    data = request.get_json()
    loan_id = data.get('loan_id', emi.loan_id)
    monthly_emi_amt = data.get('monthly_emi_amt', emi.monthly_emi_amt)
    late_fee = data.get('late_fee', 0) 
    loan = Loan.query.get(loan_id)

    if monthly_emi_amt < emi_amt:
        return jsonify({"message": "EMI amount mismatch"})

    emi.monthly_emi_amt = monthly_emi_amt
    previous_emis = EMI.query.filter(EMI.loan_id == emi.loan_id, EMI.id < emi.id).all()
    total_paid_amt = sum(prev_emi.monthly_emi_amt for prev_emi in previous_emis) + monthly_emi_amt
    emi.total_paid_amt = total_paid_amt

    emi.bal_amt = loan.loan_amount - emi.total_paid_amt
    emi.late_fee = late_fee  
    emi.current_bal = emi.bal_amt - emi.late_fee  

    db.session.commit()

    if monthly_emi_amt <= emi.total_paid_amt:
        emi.completed = True
        db.session.commit()

    return jsonify({
        "message": "EMI updated successfully",
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
