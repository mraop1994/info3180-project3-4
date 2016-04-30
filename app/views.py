import os, json, requests, base64, jwt, hashlib, uuid
from app import app, db
from flask import render_template, request, redirect, url_for, jsonify, g, session, flash, _request_ctx_stack
from werkzeug.local import LocalProxy
from flask.ext.cors import cross_origin
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from app.models import myprofile, mywish
from app.forms import LoginForm, ProfileForm, WishForm
from bs4 import BeautifulSoup
from functools import wraps


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
app.config['SECRET_KEY'] = 'super-secret'


# current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)

# # Authentication attribute/annotation
# def authenticate(error):
#   resp = jsonify(error)

#   resp.status_code = 401

#   return resp

# def requires_auth(f):
#   @wraps(f)
#   def decorated(*args, **kwargs):
#     auth = request.headers.get('Authorization', None)
#     if not auth:
#       return authenticate({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

#     parts = auth.split()

#     if parts[0].lower() != 'bearer':
#       return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
#     elif len(parts) == 1:
#       return {'code': 'invalid_header', 'description': 'Token not found'}
#     elif len(parts) > 2:
#       return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}

#     token = parts[1]
#     try:
#         payload = jwt.decode(
#             token,
#             base64.b64decode('YOUR_CLIENT_SECRET'.replace("_","/").replace("-","+")),
#             audience='YOUR_CLIENT_ID'
#         )
#     except jwt.ExpiredSignature:
#         return authenticate({'code': 'token_expired', 'description': 'token is expired'})
#     except jwt.InvalidAudienceError:
#         return authenticate({'code': 'invalid_audience', 'description': 'incorrect audience, expected: YOUR_CLIENT_ID'})
#     except jwt.DecodeError:
#         return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})

#     _request_ctx_stack.top.current_user = user = payload
#     return f(*args, **kwargs)

#   return decorated


@lm.user_loader
def load_user(id):
    return myprofile.query.get(int(id))
    

@app.before_request
def before_request():
    g.user = current_user


# def authenticate(username, password):
#     user = myprofile.query.get(username)
#     if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
#         return user

# def identity(payload):
#     user_id = payload['identity']
#     return myprofile.query.get(user_id)


# jwt = JWT(app, authenticate, identity)


# # This doesn't need authentication
# @app.route("/ping")
# @cross_origin(headers=['Content-Type', 'Authorization'])
# def ping():
#     return "All good. You don't need to be authenticated to call this"

# # This does need authentication
# @app.route("/secured/ping")
# @cross_origin(headers=['Content-Type', 'Authorization'])
# @requires_auth
# def securedPing():
#     return "All good. You only get this message if you're authenticated"


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