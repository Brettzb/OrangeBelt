from flask import Flask, render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

SCHEMA = "Belt"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
INVALID_PASSWORD_REGEX = re.compile(r'^([^0-9]*|[^A-Z]*)$')

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "This_Is_My-Secret_Key"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users/create', methods=['POST'])
def users_new():
    valid = True
    
    if len(request.form['first_name']) < 2:
        flash("First name must be longer")
        valid = False

    if len(request.form['last_name']) < 2:
        flash("Last name must be longer")
        valid = False

    if len(request.form['username']) < 3:
        flash("Username must be longer")
        valid = False

    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email must be valid")
        valid = False

    if len(request.form['password']) < 8:
        flash("Password must be at least 8 characters")
        valid = False

    if INVALID_PASSWORD_REGEX.match(request.form['password']):
        flash("Password must have at least one uppercase character and at least one number")
        valid = False
    
    if request.form['password'] != request.form['confirm']:
        flash("Passwords must match")
        valid = False

    mysql = connectToMySQL(SCHEMA)
    query = 'SELECT id FROM users WHERE username=%(username)s;'
    data = {
        'username': request.form['username']
    }
    existing_username = mysql.query_db(query, data)

    if existing_username:
        flash("Username already in use")
        valid = False
    
    mysql = connectToMySQL(SCHEMA)
    query = 'SELECT id FROM users WHERE email=%(email)s;'
    data = {
        'email': request.form['email']
    }
    existing_email = mysql.query_db(query, data)

    if existing_email:
        flash("Email already in use")
        valid = False

    if not valid:
        return redirect('/')
    
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    mysql = connectToMySQL(SCHEMA)
    query = "INSERT INTO users (first_name, last_name, email, username, pw_hash, created_at, updated_at) VALUES (%(first)s, %(last)s, %(mail)s, %(un)s, %(pw)s, NOW(), NOW());"
    data = {
        'first': request.form['first_name'],
        'last': request.form['last_name'],
        'mail': request.form['email'],
        'un': request.form['username'],
        'pw': pw_hash
    }
    user_id = mysql.query_db(query, data)
    session['user_id'] = user_id
    
    return redirect('/dash')

@app.route('/login', methods=['POST'])
def login_user():
    valid = True

    if len(request.form['email']) < 1:
        flash("Please enter your email")
        valid = False
    if len(request.form['password']) < 1:
        flash("Please enter your password")
        valid = False

    if not valid:
        return redirect('/')
    else:
        mysql = connectToMySQL(SCHEMA)
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {
            'email': request.form['email']
        }
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]['pw_hash']
            if bcrypt.check_password_hash(hashed_password, request.form['password']):
                session['user_id'] = user[0]['id']            
                return redirect("/dash")
            else:
                flash('Password invalid')
                return redirect("/")
        else:
            flash("Please enter a valid email")
            return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route("/dash")
def dash_landing():
    if 'user_id' not in session:
        return redirect('/')

    query = "SELECT * FROM users WHERE users.id = %(id)s"
    data = {'id': session['user_id']}
    mysql = connectToMySQL(SCHEMA)
    user = mysql.query_db(query, data)

    mysql = connectToMySQL(SCHEMA)
    query = "SELECT *, count(quotes_id) as likes FROM quotes JOIN users ON quotes.author = users.id LEFT JOIN users_likes_quotes ON quotes.id = users_likes_quotes.quotes_id GROUP BY quotes.id"
    quotes = mysql.query_db(query)

    mysql = connectToMySQL(SCHEMA)
    query = "SELECT * FROM users_likes_quotes WHERE users_id = %(id)s"
    data = {'id': session['user_id']}
    is_liked = mysql.query_db(query, data)
    liked_quotes = []
    for liked in is_liked:
        liked_quotes.append(liked['quotes_id'])

    print(liked_quotes)
    return render_template("dash.html", user=user[0], quotes=quotes, liked_quotes=liked_quotes)

@app.route('/post_quote', methods=['POST'])
def commit_quote():
    mysql = connectToMySQL(SCHEMA)
    print(request.form['quote_author'])
    print(request.form['quote_content'])
    query = "INSERT INTO quotes (quote_content, quote_author, author, created_at, updated_at) VALUES (%(mess)s, %(qa)s, %(aid)s, NOW(), NOW());"
    data ={
        "mess": request.form['quote_content'],
        "qa": request.form['quote_author'],
        "aid":session['user_id']
    }
    quote_id = mysql.query_db(query, data)
    return redirect("/dash")

@app.route("/like/<p_id>")
def like_quote(p_id):
    mysql = connectToMySQL(SCHEMA)
    query = "INSERT INTO users_likes_quotes (users_id, quotes_id, created_at, updated_at) VALUES (%(uid)s, %(pid)s, NOW(), NOW());"
    data = {
        'uid': session['user_id'],
        'pid': p_id
    }
    mysql.query_db(query, data)
    return redirect("/dash")

@app.route("/unlike/<p_id>")
def unlike_quote(p_id):
    mysql = connectToMySQL(SCHEMA)
    query = "DELETE FROM users_likes_quotes WHERE users_id = %(uid)s AND quotes_id = %(pid)s"
    data = {
        'uid': session['user_id'],
        'pid': p_id
    }
    mysql.query_db(query, data)
    return redirect("/dash")

@app.route("/details/<p_id>")
def quote_details(p_id):
    mysql = connectToMySQL(SCHEMA)
    query = "SELECT * FROM quotes LEFT JOIN users ON quotes.author = users.id WHERE quotes.id = %(pid)s"
    data = {
        'pid': p_id
    }
    quote = mysql.query_db(query, data)
    
    mysql = connectToMySQL(SCHEMA)
    query = "SELECT * FROM users_likes_quotes LEFT JOIN users ON users_id WHERE quotes_id = %(pid)s"
    data = {
        'pid': p_id
    }
    users_who_liked = mysql.query_db(query, data)
    return render_template("details.html", quote=quote[0], users_who_liked=users_who_liked)

@app.route("/edit")
def edit_landing():
    if 'user_id' not in session:
        return redirect('/')

    query = "SELECT * FROM users WHERE users.id = %(id)s"
    data = {'id': session['user_id']}
    mysql = connectToMySQL(SCHEMA)
    user = mysql.query_db(query, data)

    return render_template('edit.html', user=user[0])

@app.route("/post_changes", methods=['POST'])
def commit_edit():
    # valid = True
    
    # if len(request.form['first_name']) < 1:
    #     flash("First name must be longer")
    #     valid = False

    # if len(request.form['last_name']) < 1:
    #     flash("Last name must be longer")
    #     valid = False

    # if not EMAIL_REGEX.match(request.form['email']):
    #     flash("Email must be valid")
    #     valid = False
    
    # mysql = connectToMySQL(SCHEMA)
    # query = 'SELECT id FROM users WHERE email=%(email)s;'
    # data = {
    #     'email': request.form['email']
    # }
    # existing_email = mysql.query_db(query, data)
    
    # if existing_email:
    #     flash("Email already in use")
    #     valid = False

    # if not valid:
    #     return redirect('/dash')
    
    mysql = connectToMySQL(SCHEMA)
    query = "UPDATE users SET first_name= %(fn)s, last_name=%(ln)s, email=%(em)s, created_at=NOW(), updated_at=NOW() WHERE id=%(id)s;"
    data ={
        "id": session['user_id'],
        "fn": request.form['first_name'],
        "ln": request.form['last_name'],
        "em": request.form['email']
    }
    update = mysql.query_db(query, data)

    return redirect('/dash')

@app.route("/user/<u_id>")
def user_details(u_id):
    mysql = connectToMySQL(SCHEMA)
    query = "SELECT * FROM users LEFT JOIN quotes"

    users = mysql.query_db(query)
    
    
    mysql = connectToMySQL(SCHEMA)
    query = "SELECT quote_content FROM quotes INNER JOIN users ON quotes.author = users.id;"
    
    quote_content = mysql.query_db(query)

    return render_template("user.html", quote_content=quote_content, users=users)



if __name__ == "__main__":
    app.run(debug=True)