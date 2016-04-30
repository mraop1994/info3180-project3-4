import os, json, requests, hashlib, uuid
from app import app, db
from flask import render_template, request, redirect, url_for, jsonify, g, session, flash
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from app.models import myprofile, mywish
from app.forms import LoginForm, ProfileForm, WishForm
from bs4 import BeautifulSoup


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
app.config['SECRET_KEY'] = 'super-secret'


@lm.user_loader
def load_user(id):
    return myprofile.query.get(int(id))
    

@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
def home():
    """Render website's home page."""
    if g.user.is_authenticated:
        return redirect('/api/user/' + str(g.user.hashed) + '/wishlist')
    return render_template('home.html')
    

@app.route('/api/user/login', methods=['POST','GET'])
def login():
    error=None
    form = LoginForm(request.form)
    if request.method == 'POST':
        attempted_email = request.form['email']
        attempted_password = request.form['password']
        db_creds = myprofile.query.filter_by(email=attempted_email).first()
        db_email = db_creds.email
        db_password = db_creds.password
        db_id = db_creds.hashed
        if attempted_email == db_email and attempted_password == db_password:
            login_user(db_creds)
            flash("Welcome to your wishlist")
            return redirect('/api/user/' + str(db_id) + '/wishlist')
        else:
            error = 'Invalid credentials'
            return render_template("home.html",error=error,form=form)
    form = LoginForm()
    return render_template("home.html",error=error,form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/api/user/register', methods = ['POST','GET'])
def newprofile():
    error=None
    if session['logged_in']:
        form = ProfileForm()
        if request.method == 'POST':
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            sex = request.form['sex']
            age = int(request.form['age'])
            email = request.form['email']
            password = request.form['password']
            salt = uuid.uuid4().hex
            salty = hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt
            hash_object = hashlib.sha256(email + salty)
            hashed = hash_object.hexdigest()
            newProfile = myprofile(firstname=firstname, lastname=lastname, email=email, password=password, sex=sex, age=age, hashed=hashed)
            db.session.add(newProfile)
            db.session.commit()
            return redirect('/')
        form = ProfileForm()
        return render_template('registration.html',form=form,error=error)
    return redirect('/')


@app.route('/api/user/<userid>')
@login_required
def profile_view(userid):
    if g.user.is_authenticated:
        form = WishForm()
        profile_vars = {'id':g.user.userid, 'email':g.user.email, 'age':g.user.age, 'firstname':g.user.firstname, 'lastname':g.user.lastname, 'sex':g.user.sex, 'hashed':g.user.hashed}
        return render_template('addWish.html',form=form,profile=profile_vars)
    

@app.route('/api/user/<id>/wishlist', methods = ['POST','GET'])
@login_required
def wishlist(id):
    profile = myprofile.query.filter_by(hashed=id).first()
    profile_vars = {'id':profile.userid, 'email':profile.email, 'age':profile.age, 'firstname':profile.firstname, 'lastname':profile.lastname, 'sex':profile.sex, 'hashed':g.user.hashed}
    form = WishForm()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        url = request.form['url']
        newWish = mywish(userid=g.user.userid, title=title, description=description, description_url=url)
        db.session.add(newWish)
        db.session.commit()
        return redirect(url_for('getPics',wishid=newWish.wishid))
    if request.method == "GET":
        wish = mywish.query.filter_by(userid=profile.userid)
        wishes = []
        for wishy in wish:
            wish_vars = {'wishid':wishy.wishid, 'userid':wishy.userid, 'title':wishy.title, 'desc':wishy.description, 'descurl':wishy.description_url, 'thumbs':wishy.thumbnail_url}
            wishes.append(wish_vars)
        return render_template('profile_view.html', wish=wishes, profile=profile_vars)
    return render_template('addWish.html',form=form,profile=profile_vars)

    
@app.route('/api/thumbnail/process/<wishid>')
@login_required
def getPics(wishid):
    wish = mywish.query.filter_by(wishid=wishid).first()
    wish_vars = {'wishid':wish.wishid, 'userid':g.user.userid, 'title':wish.title, 'desc':wish.description, 'descurl':wish.description_url, 'thumbs':wish.thumbnail_url}
    profile_vars = {'id':g.user.userid, 'email':g.user.email, 'age':g.user.age, 'firstname':g.user.firstname, 'lastname':g.user.lastname, 'sex':g.user.sex, 'hashed':g.user.hashed}
    url = wish.description_url
    result = requests.get(url)
    data = result.text
    images = []
    soup = BeautifulSoup(data, 'html.parser')
    og_image = (soup.find('meta', property='og:image') or soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        images.append(og_image['content'])
    for img in soup.find_all("img", class_="a-dynamic-image"):
        print img['src']
        images.append(img['src'])
    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        images.append(thumbnail_spec['href'])
    for img in soup.find_all("img", class_="a-dynamic-image"):
        if "sprite" not in img["src"]:
            images.append(img['src'])
    return render_template('pickimage.html',images=images,wish=wish_vars,profile=profile_vars)


@app.route('/addpic/<wishid>', methods=['POST'])
@login_required
def wishpic(wishid):
    user = mywish.query.get(wishid)
    user.thumbnail_url = request.json['thumbs']
    db.session.commit()
    if user.thumbnail_url == request.json['thumbs']:
        flash("Wish successfully added.")
    else:
        flash("Wish not added, some error occurred.")
    return redirect('/api/user/' + str(g.user.hashed) + '/wishlist')


@app.route('/api/user/sharing')
def sharing():
    return render_template('sharing.html')
    

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()