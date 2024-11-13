import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

baseDir = os.path.abspath(os.path.dirname(__file__))
dirDatabase = os.path.join(baseDir, 'database.db')
print("Path database is:", dirDatabase)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + dirDatabase
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
def create_db(app):
    if not os.path.exists(dirDatabase):
        with app.app_context():
            db.create_all()
        print("Created db!")
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    create_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    

# route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email_login")
        password = request.form.get("password_login")
        print('----------Login with account------------','Username: ', email, 'Password: ', password)
        users = User.query.all();
        print(users)
        if len(users) == 0:
            return render_template("login_register.html", errorMessage = 'Tài khoản / Mật khẩu không chính xác') 
        for user in users:
            if(user.email == email and user.password == password):
                return 'Login successful'
            else:
                return render_template("login_register.html", errorMessage = 'Tài khoản / Mật khẩu không chính xác') 
    else:
        return render_template("login_register.html")
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form.get("firstName_register")
        lastName = request.form.get("lastName_register")
        userName = request.form.get("userName_register")
        password = request.form.get("password_register")
        confirmPass = request.form.get("confirmPassword")
        if password != confirmPass:
            return render_template("login-register.html", errorMessage2 = 'Mật khẩu không trùng khớp') 
        else:
            user = User(firstName = firstName,
            lastName = lastName,
            email = userName,
            password = password)
        db.session.add(user)
        db.session.commit()
        return render_template("login_register.html")
    else:
        return render_template("login_register.html")
    
@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")

@app.route("/shop", methods=['GET'])
def shop():
    return render_template("shop.html")

@app.route("/about-us", methods=['GET'])
def about_us():
    return render_template("about-us.html")

@app.route("/contact", methods=['GET'])
def contact():
    return render_template("contact.html")

@app.route("/blog", methods=['GET'])
def blog():
    return render_template("blog.html")


if __name__ == '__main__':
    create_db(app)
    app.run(debug=True, port=5000)