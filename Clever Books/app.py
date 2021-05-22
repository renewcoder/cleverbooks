from flask import Flask, request, render_template, flash, redirect, url_for, session
import sqlite3
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
	return render_template('index.html')
 

@app.route('/profile')
def profile():
	return render_template('profile.html')
    
    
@app.route('/loginerror')
def loginerror():
	return render_template('loginerror.html')


@app.route('/adminpanel')
def adminpanel():
	return render_template('/admin/adminpanel.html')
@app.route('/books')
def books():
	return render_template('/admin/books.html')
@app.route('/users')
def users():
	return render_template('/admin/users.html')
    
@app.route('/search')
def search():
	return render_template('search.html')



class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	user_type = StringField('User Type', [validators.Length(min=1, max=50)])
	phone = StringField('Phone', [validators.Length(min=1, max=50)])

	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Password do not match')
	])
	confirm = PasswordField('Confirm Password')
    
class AdminRegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	user_type = StringField('User Type', [validators.Length(min=1, max=50)])

	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Password do not match')
	])
	confirm = PasswordField('Confirm Password')

class AddBooks(Form):
	isbn = StringField('isbn', [validators.Length(min=1, max=100)])
	booktitle = StringField('booktitle', [validators.Length(min=1, max=100)])
	bookauthor = StringField('bookauthor', [validators.Length(min=1, max=100)])
	yearsofpublication = StringField('yearsofpublication', [validators.Length(min=1, max=100)])
	publisher = StringField('publisher', [validators.Length(min=1, max=100)])
	imageurl = StringField('imageurl', [validators.Length(min=1, max=100)])


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		phone = form.phone.data
		user_type = form.user_type.data
	
		password = sha256_crypt.encrypt(str(form.password.data))

		connection = sqlite3.connect('test.db')
		cursor = connection.cursor()
		cursor.execute("INSERT INTO users(name,email,password,phone,user_type) VALUES('"+name+"','"+email+"','"+password+"','"+phone+"','"+user_type+"')")
		connection.commit()
		connection.close()

		

		return redirect(url_for('login'))       

	return render_template('register.html', form=form)



@app.route('/adminregister', methods=['GET', 'POST'])
def adminregister():
	form = AdminRegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		user_type = form.user_type.data
		phone = form.phone.data
	
		password = sha256_crypt.encrypt(str(form.password.data))

		connection = sqlite3.connect('test.db')
		cursor = connection.cursor()
		cursor.execute("INSERT INTO users(name,email,password,phone,user_type) VALUES('"+name+"','"+email+"','"+password+"','"+phone+"','"+user_type+"')")
		connection.commit()
		connection.close()

		flash('User Registered Successfully', 'success')

		return redirect(url_for('adminpanel'))       

	return render_template('/admin/adminpanel.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password_candidate = request.form['password']
		user_type = request.form['user_type']
		name = request.form['name']
		phone = request.form['phone']

		connection = sqlite3.connect('test.db')
		cursor = connection.cursor()
		result = cursor.execute("SELECT * FROM users WHERE email = '"+email+"'")
		if result.arraysize > 0:
			data = cursor.fetchone()
			password = data[3]
			user_type = data[5]
			name = data[1]
			phone = data[4]
			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('PASSWORD MATCHED')
				session['logged_in'] = True
				session['email'] = email
				session['user_type'] = user_type
				session['name'] = name
				session['phone'] = phone

				flash('You are Logged in to Admin Panel', 'success')

				return redirect(url_for('search'))

			else:
				app.logger.info('PASSWORD NOT MATCHED')
				error = 'Incorrect Password'
				return render_template('login.html', error=error)

			cursor.close()
		else:
			app.logger.info('NO USER')
			error = 'Username not found'
			return render_template('login.html', error=error)

	return render_template('login.html')


def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap



@app.route('/updateuser', methods = ['POST'])
def updateuser():
    if request.method == "POST":
        my_data = users.query.get(request.form.get('id'))
        my_data.name = request.form['name']
        my_data.email = request.form['email']
        my_data.password = request.form['password']
        my_data.user_type = request.form['user_type']
        my_data.phone = request.form['phone']
        db.session.commit()
        flash("User Updated Successfully")
        return redirect(url_for('adminpanel'))

@app.route('/delete/<id>/')
def deleteuser(id):
    my_data=users.query.get(id)
    db.session.delete(users)
    db.session.commit()    
    flash("User Data Deleted Successfully")
    return redirect(url_for('adminpanel'))
    
    
@app.route('/addbook', methods = ['POST'])
def addbook():
	form = AddBooks(request.form)
	if request.method == 'POST' and form.validate():
		isbn = form.isbn.data
		booktitle = form.booktitle.data
		bookauthor = form.bookauthor.data
		yearsofpublication = form.yearsofpublication.data
		publisher = form.publisher.data
		imageurl = form.publisher.data
	

		connection = sqlite3.connect('test.db')
		cursor = connection.cursor()
		cursor.execute("INSERT INTO books(isbn,booktitle,bookauthor,yearsofpublication,publisher,imageurl) VALUES('"+isbn+"','"+booktitle+"','"+bookauthor+"','"+yearsofpublication+"','"+publisher+"','"+imageurl+"')")
		connection.commit()
		connection.close()

		flash('Book Data Inserted Successfully', 'success')

		return redirect(url_for('books'))      

	return redirect(url_for('books'))



@app.route('/updatebook', methods = ['POST'])
def updatebook():
    if request.method == "POST":
        my_data = users.query.get(request.form.get('id'))
        my_data.isbn = request.form['isbn']
        my_data.booktitle = request.form['booktitle']
        my_data.bookauthor = request.form['bookauthor']
        my_data.yearsofpublication = request.form['yearsofpublication']
        my_data.publisher = request.form['publisher']
        my_data.imageurl = request.form['imageurl']
        db.session.commit()
        flash("User Updated Successfully")
        return redirect(url_for('adminpanel'))

@app.route('/delete/<id>/')
def deletebook(id):
    my_data=books.query.get(id)
    db.session.delete(books)
    db.session.commit()
    
    flash("User Data Deleted Successfully")
    return redirect(url_for('adminpanel'))
    
    
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	return redirect(url_for('login'))


if __name__ == '__main__':
	app.secret_key = "themagician"
	app.run()
