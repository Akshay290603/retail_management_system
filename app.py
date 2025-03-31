from flask import Flask, render_template
from flask_login import LoginManager, UserMixin, current_user, login_required

app = Flask(__name__)
app.secret_key = "1234"

# # Initialize Flask-Login
# login_manager = LoginManager()
# login_manager.init_app(app)

# # Dummy user class for demonstration
# class User(UserMixin):
#     def __init__(self, id):
#         self.id = id

# # Load user function
# @login_manager.user_loader
# def load_user(user_id):
#     return User(user_id)

@app.route('/')
def index():
    return "Welcome to the Retail Management System!"

@app.route('/layout')
# @login_required
def layout():
    return render_template('layout.html')

@app.route('/login')
def login():
    return "Login Page"

@app.route('/register')
def register():
    return "Register Page"

@app.route('/logout')
def logout():
    return "Logout Page"

@app.route('/customer/home')
@app.route('/customer/category')
def category():
    return render_template('customer/category.html')

if __name__ == "__main__":
    app.run(debug=True)

