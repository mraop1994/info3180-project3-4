import os, time, datetime, json, requests, urlparse, urllib2
from app import app, db
from flask import render_template, request, redirect, url_for, jsonify, g, session, flash
from flask.ext.login import LoginManager, login_user , logout_user , current_user , login_required
from app.models import myprofile, mywish
from app.forms import LoginForm, ProfileForm, WishForm
from werkzeug.utils import secure_filename
from functools import wraps
from bs4 import BeautifulSoup


app.secret_key = 'why would I tell you my secret key?'
app.config.from_object(__name__)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return myprofile.query.get(int(id))
    

@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')
    

@app.route('/login', methods=['POST','GET'])
def login():
    error=None
    form = LoginForm(request.form)
    if request.method == 'POST':
        attempted_email = request.form['email']
        attempted_password = request.form['password']
        db_creds = myprofile.query.filter_by(email=attempted_email).first()
        db_email = db_creds.email
        db_password = db_creds.password
        db_id = db_creds.userid
        if attempted_email == db_email and attempted_password == db_password:
            session['logged_in'] = True
            login_user(db_creds)
            return redirect('/profile/'+str(db_id))
        else:
            error = 'Invalid credentials'
            return render_template("home.html",error=error,form=form)
    form = LoginForm()
    return render_template("home.html",error=error,form=form)


@app.route('/logout')
def logout():
    logout_user()
    session['logged_in'] = False
    return redirect('/')


@app.route('/profile/', methods = ['POST','GET'])
def newprofile():
    if request.method == 'POST':
        form = ProfileForm()
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        sex = request.form['sex']
        age = int(request.form['age'])
        email = request.form['email']
        password = request.form['password']
        newProfile = myprofile(firstname=firstname, lastname=lastname, email=email, password=password, sex=sex, age=age)
        db.session.add(newProfile)
        db.session.commit()
        profilefilter = myprofile.query.filter_by(email=newProfile.email).first()
        return redirect('/profile/'+str(profilefilter.userid))
    form = ProfileForm()
    return render_template('registration.html',form=form)


@app.route('/profile/<userid>')
@login_required
def profile_view(userid):
    if g.user.is_authenticated:
        profile_vars = {'id':g.user.userid, 'email':g.user.email, 'age':g.user.age, 'firstname':g.user.firstname, 'lastname':g.user.lastname, 'sex':g.user.sex}
        return render_template('profile_view.html',profile=profile_vars)
    

@app.route('/addWish/', methods = ['POST','GET'])
def addWish():
    # profile = myprofile.query.filter_by(userid=userid).first()
    # profile_vars = {'id':profile.userid, 'email':profile.email, 'age':profile.age, 'firstname':profile.firstname, 'lastname':profile.lastname, 'sex':profile.sex}
    if request.method == 'POST':
        form = WishForm()
        url = request.form['url']
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
        return render_template('pickimage.html',images=images)
        
        # def image_dem():
        #     image = """<img src="%s"><br />"""
        #     for img in soup.find_all("img", class_="a-dynamic-image"):
        #       if "sprite" not in img["src"]:
        #           print image % urlparse.urljoin(url, img["src"])
        #           print img['src']
        # image_dem()
        
        
        # title = request.form['title']
        # description = request.form['description']
        # url = request.form['url']
        # return redirect(url_for('getPics'))
    #     newWish = mywish(userid=userid, title=title, description=description, description_url=description_url)
    #     db.session.add(newWish)
    #     db.session.commit()
    #     profilefilter = myprofile.query.filter_by(userid=newWish.userid).first()
    #     return redirect('/profile/'+str(profilefilter.userid))
    form = WishForm()
    return render_template('addWish.html',form=form)
    
    
# @app.route('/getPics', methods = ['POST','GET'])
# def getPics():
#     form = WishForm()
#     url = request.form['url']
#     result = requests.get(url)
#     data = result.text
#     soup = BeautifulSoup(data, 'html.parser')
#     og_image = (soup.find('meta', property='og:image') or
#                         soup.find('meta', attrs={'name': 'og:image'}))
#     if og_image and og_image['content']:
#         print og_image['content']
    
#     thumbnail_spec = soup.find('link', rel='image_src')
#     if thumbnail_spec and thumbnail_spec['href']:
#         print thumbnail_spec['href']
    
#     def image_dem():
#         image = """<img src="%s"><br />"""
#         for img in soup.find_all("img", class_="a-dynamic-image"): #soup.findAll("img", src=True):
#           if "sprite" not in img["src"]:
#               print image % urlparse.urljoin(url, img["src"])
#               print img['src']
#     image_dem()
#     return redirect('/profile/')


@app.route('/addWish/<theimage>', methods = ['POST','GET'])
def popDBwish(theimage):
    print theimage['1']
    return render_template(url_for('/'))


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
