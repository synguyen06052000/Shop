import os
from flask import Flask, render_template, request, url_for, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask import session
from sqlalchemy.sql import func
from werkzeug.utils import secure_filename
import imgbbpy, random, shutil

baseDir = os.path.abspath(os.path.dirname(__file__))
dirDatabase = os.path.join(baseDir, 'database.db')
print("Path database is:", dirDatabase)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + dirDatabase
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "b9ZHtEpIeiKHuM9"
app.config['SESSION_TYPE'] = "filesystem"

db = SQLAlchemy(app)
Session(app)


def randomIdImage():
    return random.randint(1000, 9999)

def create_db(app):
    with app.app_context():
        db.create_all()
        print("Created db!")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100), nullable=False)
    lastName = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    create_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idBlog = db.Column(db.Integer, nullable=False, default=1)
    idCommenter = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(10000), nullable=False)
    create_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(10000), nullable=False)
    name = db.Column(db.String(10000), nullable=False)
    new = new = db.Column(db.Boolean, nullable=False)
    price = db.Column(db.Float, nullable=False)
    saleTime = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Integer, nullable=False)
    percentSale = db.Column(db.Integer, nullable=False)
    dimension = db.Column(db.String(10000), nullable=False)
    img = db.Column(db.String(10000), nullable=False)


@app.route("/delete_product/<int:product_id>")
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    #return redirect(url_for('home'))

# route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email_login")
        password = request.form.get("password_login")
        users = User.query.all()
        for user in users:
            print(user.password, check_password_hash(user.password,password))
            if(user.email == email and check_password_hash(user.password, password)):
                session['userId'] = user.id
                session['username'] = user.lastName + ' ' + user.firstName
                session['email'] = user.email
                return redirect(url_for('home'))
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
            password = generate_password_hash(password)
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
    products = Product.query.all()
    hotDealProducts = []
    laptops = []
    tvs = []
    hotDealCount = min(len(products), 4)
    laptopTvCount = min(len(products), 6)
    
    hotDealProducts = products[:hotDealCount]
    laptops = products[:laptopTvCount]
    tvs = products[:laptopTvCount]
    return render_template("index.html", hotDealProducts=hotDealProducts, laptops=laptops, tvs=tvs)

@app.route("/single-product", methods=['GET'])
def single_product():
    return render_template("single-product.html")

@app.route("/shopping-cart", methods=['GET'])
def shopping_cart():
    return render_template("shopping-cart.html")

@app.route("/shop", methods=['GET'])
def shop():
    return render_template("shop.html")

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('userId', None)
    session.pop('username', None)
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route("/about-us", methods=['GET'])
def about_us():
    return render_template("about-us.html")

@app.route("/contact", methods=['GET'])
def contact():
    return render_template("contact.html")

@app.route("/blog", methods=['GET'])
def blog():
    return render_template("blog.html")

@app.route("/blog-detail", methods=['GET'])
def blog_detail():
    currentBlog = 1 #Get currentBlog to get all comment in this blog
    comments = Comment.query.all()
    listComment = []
    for comment in comments:
        if comment.idBlog == currentBlog:
            commentByUser = {}
            user = User.query.get_or_404(comment.idCommenter)
            print("Get user from comment", user.id)
            commentByUser['name'] = user.firstName + " " + user.lastName
            commentByUser['userId'] = comment.idCommenter
            commentByUser['text'] = comment.comment
            commentByUser['createAt'] = comment.create_at
            listComment.append(commentByUser)
    return render_template("blog-details.html", listComment=listComment, commentSize=len(comments))

@app.route("/blog-detail/comment/", methods=['POST'])
def add_comment():
    if 'username' in session:
        comment_text = request.form.get("comment")
        userId = session.get('userId')
        if comment_text:
            new_comment = Comment(idCommenter=userId, comment=comment_text)
            db.session.add(new_comment)
            db.session.commit()
        return redirect(url_for('blog_detail'))
    else:
        return redirect(url_for('login'))

@app.route("/add_to_cart/<int:product_id>", methods=['POST', 'GET'])
def add_to_cart(product_id):
    print("Thêm vào giỏ hàng", product_id)
    
    if request.method == 'POST':
        print("Hello World!")
    if 'cart' not in session:
        session['cart'] = []
    
    session['cart'].append(product_id)
    session.modified = True
    #return make_response('', 204)
    return redirect(url_for('home'))


# Admin
@app.route("/admin", methods=['GET'])
def admin_home():
    return render_template("base_admin.html")

@app.route("/update_info_user/<int:user_id>", methods=['GET', 'POST'])
def admin_update_info_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user_firstName = request.form.get('firstName')
        user_lastName = request.form.get('lastName')
        user_email = request.form.get('email')
        
        user.firstName = user_firstName
        user.lastName = user_lastName
        user.email = user_email
        
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin_manager_user'))
    
    return render_template("base_admin.html")

@app.route("/delete_user/<int:user_id>")
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)      
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_manager_user'))

@app.route("/admin_manager_user", methods=['GET'])
def admin_manager_user():
    users = User.query.all()
    return render_template("admin_manager_user.html", users=users)

@app.route("/admin_manager_product", methods=['GET'])
def admin_manager_product():
    products = Product.query.all()
    return render_template("admin_manager_product.html", products=products)

@app.route("/add_product", methods=['GET', 'POST'])  
def add_product():
    client = imgbbpy.SyncClient('ffbdad501d7316f58281c592a65a955f')
    if request.method == 'POST':
        productCategory = request.form.get("productCategory")
        productName = request.form.get("productName")
        productPrice = float(request.form.get("productPrice"))
        productSaleTime = int(request.form.get("productSaleTime"))
        productRate = int(request.form.get("productRate"))
        productPercentSale = int(request.form.get("productPercentSale"))
        productDimension = request.form.get("productDimension")
        img = request.files["productImage"]
        
        directory_img = str(randomIdImage())
        path = os.path.join('backend','static', 'ImageToUpload', directory_img)
        os.makedirs(path)
        fileName = secure_filename(img.filename) #Mã hóa tên file
        img.save(os.path.join(path, fileName)) #Lưu file vào local
        imageCloud = client.upload(file=os.path.join(path, fileName))
        shutil.rmtree(path, ignore_errors=True)
        
        product = Product(category=productCategory,
                          name=productName, 
                          new=True, 
                          price=float(productPrice), 
                          saleTime=productSaleTime, 
                          rate=productRate, 
                          percentSale=productPercentSale, 
                          dimension=productDimension, 
                          img=imageCloud.url)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('home'))
        
    return render_template("add_product.html")

@app.route("/update_product/<int:product_id>", methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        productCategory = request.form.get("productCategory")
        productName = request.form.get("productName")
        productPrice = float(request.form.get("productPrice"))
        productSaleTime = int(request.form.get("productSaleTime"))
        productRate = int(request.form.get("productRate"))
        productPercentSale = int(request.form.get("productPercentSale"))
        productDimension = request.form.get("productDimension")
        
        product.category = productCategory
        product.name = productName
        product.price = productPrice
        product.saleTime = productSaleTime
        product.rate = productRate
        product.percentSale = productPercentSale
        product.dimension = productDimension
        
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('admin_manager_product'))
    return redirect(url_for('admin_home'))

@app.route("/delete_product/<int:product_id>", methods=['GET'])
def admin_delete_product(product_id):
    products = Product.query.get_or_404(product_id)
    db.session.delete(products)
    db.session.commit()
    return render_template("admin_manager_product.html", products=products)

@app.route("/admin_manager_order", methods=['GET'])
def admin_manager_order():
    return render_template("admin_manager_order.html")

if __name__ == '__main__':
    create_db(app)
    app.run(debug=True, port=5000)