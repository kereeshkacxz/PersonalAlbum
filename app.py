from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
from database import Users, Images
import os
import datetime
import shutil
app = Flask(__name__)

ImagesTable = Images()
UsersTable = Users()

salt_password = "salt123909321".encode("utf-8")
salt_image = "imageshjiasd!!".encode("utf-8")
SECRET_KEY = 'fbe98564795c5c0a492e4b2e46e7cfb03e72a3940eddeadaad5ff9b5ddd2da8d'
UPLOAD_FOLDER = "static/upload"
ALLOWED_EXTENSIONS = set(['.bmp', '.gif', '.png', '.jpg', '.jpeg', '.webp'])

def check_validation_login(login):
    if not login or len(login) > 16:
        return False
    if not("a" <= login[0] <= "z" or "A" <= login[0] <= "Z"):
        return False
    for i in login:
        if not(("a" <= i <= "z") or ("A" <= i <= "Z") or (i == "_") or ("0" <= i <= "9")):
            return False
    return True

def check_validation_password(password):
    if not password or len(password) < 6:
        return False
    for i in password:
        if not(("a" <= i <= "z") or ("A" <= i <= "Z") or (i == "_") or ("0" <= i <= "9")):
            return False
    return True

def check_validation_extension(file):
    return os.path.splitext(file.filename)[1] in ALLOWED_EXTENSIONS

def check_user():
    if not "login" in session or not "auth" in session:
        return False
    if not session["auth"]:
        return False
    if not UsersTable.CheckUser(session["login"]):
        return False
    return True

@app.errorhandler(404)
def page_not_found(e):
    if check_user():
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))


@app.route("/loginHandle", methods = ["POST"])
def authorization():
    if check_user():
        return redirect(url_for("main"))

    login = request.form.get('login')
    password = request.form.get('password')

    if not check_validation_login(login):
        return redirect(url_for("login", flag = 1))
    
    if not check_validation_password(password):
        return redirect(url_for("login", flag = 2))
    
    user = UsersTable.Select(login)
    
    if not user:
        return redirect(url_for("login", flag = 4))
    password_hash = hashlib.sha256()
    password_hash.update(password.encode("utf-8"))
    password_hash.update(salt_password)
    if password_hash.hexdigest() != user[1]:
        return redirect(url_for("login", flag = 3))
    if login not in session:
        session['login'] = login
        session['auth'] = True
        session["page"] = 0

    return redirect(url_for("main"))


@app.route("/registerHandle", methods = ["POST"])
def registration():
    if check_user():
        return redirect(url_for("main"))
    login = request.form.get('login')
    password = request.form.get('password')
    
    if not check_validation_login(login):
        return redirect(url_for("register", flag = 2))
    
    if not check_validation_password(password):
        return redirect(url_for("register", flag = 3))

    user = UsersTable.Select(login)

    if user:
        return redirect(url_for("register", flag = 1))
    
    password_hash = hashlib.sha256()
    password_hash.update(password.encode("utf-8"))
    password_hash.update(salt_password)
    UsersTable.Insert(login, password_hash.hexdigest())
    if os.path.exists(UPLOAD_FOLDER+"/"+login):
        shutil.rmtree(UPLOAD_FOLDER+"/"+login)
    os.mkdir(UPLOAD_FOLDER+"/"+login)
    return redirect(url_for("login", flag = 5))


@app.route("/login")
@app.route("/login/<int:flag>")
def login(flag = 0):
    if check_user():
        return redirect(url_for("main"))
    return render_template("Login.html", flag = flag)


@app.route("/register")
@app.route("/register/<int:flag>")
def register(flag = 0):
    if check_user():
        return redirect(url_for("main"))
    return render_template("Register.html", flag = flag)

@app.route("/setpage/<int:page>")
def setPage(page = 0):
    if not check_user():
        return redirect(url_for("login"))
    session['page'] = page
    return redirect(url_for("main"))

@app.route("/")
def main():
    # print(session)
    if not check_user():
        return redirect(url_for("login"))
    ImageForPage = 3
    img = ImagesTable.SelectByLogin(session["login"])

    if len(img) == 0:
        session['page'] = 1
        return render_template('Main.html', img = img, page = session['page'], lastPage = 1, login = session["login"])
    
    lastPage = len(img)//ImageForPage + (0 if len(img) % ImageForPage == 0 else 1)

    if session['page'] > lastPage:
        session['page'] = lastPage
    
    if session['page'] < 1:    
        session['page'] = 1
    
    start = ImageForPage*(session['page'] - 1)
    end = ImageForPage*session['page']
    img = img[start:end]
    return render_template('Main.html', img = img, page = session['page'], lastPage = lastPage, login = session["login"])

@app.route('/addimageHandle', methods=["POST"])
def addImageHandle():
    if not check_user():
        return redirect(url_for("login"))

    if "flag" in request.form:
        name = request.form.get('name')
        caption = request.form.get('caption')
        cur_time = datetime.datetime.now().strftime('%d_%m_%y_%H_%M_%S_%f_')
        filename = "test"
        ImagesTable.Insert(name, caption, session["login"], filename)
        return redirect(url_for("main"))

    name = request.form.get('name')
    caption = request.form.get('caption')
    file = request.files['imagefile']
    if file == '' or name == '' or not check_validation_extension(file):
        return redirect(url_for("addImage", flag = 1))
    imageId = ImagesTable.TakeMaxIndex() + 1
    filename = hashlib.sha256()
    filename.update(str(imageId).encode("utf-8"))
    filename.update(salt_image)
    cur_time = datetime.datetime.now().strftime('%d_%m_%y_%H_%M_%S_%f_')
    ImagesTable.Insert(name, caption, session["login"], str(cur_time)+filename.hexdigest())
    if imageId:
        file.save(os.path.join(UPLOAD_FOLDER+"/"+session["login"], str(cur_time)+filename.hexdigest()))
    return redirect(url_for("main"))

@app.route('/addimage')
@app.route('/addimage/<int:flag>')
def addImage(flag = 0):
    if not check_user():
        return redirect(url_for("login"))
    return render_template('AddImage.html', flag = flag)

@app.route('/editimage/<int:idImage>')
def editImage(idImage):
    if not check_user():
        return redirect(url_for("login"))
    
    if not ImagesTable.CheckAuthor(idImage, session["login"]):
        return redirect(url_for("main"))
    curImg = ImagesTable.SelectById(idImage)
    if len(curImg) != 1:
        return redirect(url_for("main"))
    return render_template('EditImage.html', curImg= curImg[0], login= session["login"])

@app.route('/editimageHandle/<int:idImage>', methods=["POST"])
def editImageHandle(idImage):
    if not check_user():
        return redirect(url_for("login"))
    
    if not ImagesTable.CheckAuthor(idImage, session["login"]):
        return redirect(url_for("main"))
    
    name = request.form.get('name')
    caption = request.form.get('caption')
    if name != '' and caption !='':
        ImagesTable.Update(idImage, name, caption)
    return redirect(url_for("main"))

@app.route('/deleteimageHandle/<int:idImage>')
def deleteImageHandle(idImage):
    if not check_user():
        return redirect(url_for("login"))
    
    if not ImagesTable.CheckAuthor(idImage, session["login"]):
        return redirect(url_for("main"))
    
    result = ImagesTable.Delete(idImage)
    if result:
        if os.path.exists(os.path.join(UPLOAD_FOLDER+"/"+session["login"], result[3])):
            os.remove(os.path.join(UPLOAD_FOLDER+"/"+session["login"], result[3]))
    return redirect(url_for("main"))

@app.route('/logoutHandle')
def logoutHandle():
    if not check_user():
        return redirect(url_for("login"))
    del session["login"]
    session["auth"] = False
    del session["page"]
    return redirect(url_for("login"))


app.secret_key = SECRET_KEY
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(days=31)

if __name__ == '__main__':
    app.run()