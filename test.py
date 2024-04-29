from app import app
import pytest
from database import Users,Images
from database_test import Users_test,Images_test


@pytest.fixture
def test_client():
    app.testing = True
    client = app.test_client()
    return client

@pytest.fixture
def db_test():
    users = Users_test()
    images = Images_test()
    return {"users":users, "images":images}

@pytest.fixture
def db():
    users = Users()
    images = Images()

    return {"users":users, "images":images}

def login(test_client):
    response = test_client.post("/loginHandle", data={ "login": "test_pytest", "password": "test_pytest"}, follow_redirects = True)
    return response

# Функциональные тесты

# Проверяем авторизацию
def test_login(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == "/"

# Проверяем авторизацию с паролем неверного формата
def test_login_password_incorrect(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "111"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/login/2'

# Проверяем авторизацию с неверным паролем
def test_login_wrong_password(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "asdasd"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/login/3'

# Проверяем авторизацию с логином неверного формата
def test_login_login_incorrect(test_client):
    response = test_client.post("/loginHandle", data={ "login": "1admin", "password": "111"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/login/1'

# Проверяем авторизацию пользователя, которого не существует
def test_login_user_not_exists(test_client):
    response = test_client.post("/loginHandle", data={ "login": "sadadmin", "password": "111123"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/login/4'



# Проверяем регистрацию
def test_register(test_client, db):
    response = test_client.post("/registerHandle", data={ "login": "pytest_test", "password": "pytest_test"}, follow_redirects = True)
    db["users"].Delete("pytest_test")
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/login/5'

# Проверяем регистрацию с паролем неверного формата
def test_register_password_incorrect(test_client):
    response = test_client.post("/registerHandle", data={ "login": "admin", "password": "111"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/register/3'

# Проверяем регистрция с логином неверного формата
def test_register_login_incorrect(test_client):
    response = test_client.post("/registerHandle", data={ "login": "1admin", "password": "111"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/register/2'

# Проверяем регистрация пользователя, которого не существует
def test_register_user_exists(test_client):
    response = test_client.post("/registerHandle", data={ "login": "admin", "password": "111123"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].status_code == 302
    assert response.history[0].headers["Location"] == '/register/1'



# Проверяем логаут
def test_logout(test_client):
    assert login(test_client).status_code == 200
    response = test_client.get('/logoutHandle')
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

# Проверяем логаут без авторизации
def test_logout_without_login(test_client):
    response = test_client.get('/logoutHandle')
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"



# Проверяем вставку картинки и удаление
def test_images_add(test_client, db):
    assert login(test_client).status_code == 200
    response = test_client.post("/addimageHandle", data={ "name": "test", "caption": "test", "flag":"True"}, follow_redirects = True)
    db["images"].DeleteByUser("test_pytest")
    assert response.status_code == 200
    assert response.history[0].headers["Location"] == "/"
    
#Проверяем вставку картинки без авторизации 
def test_images_add_without_login(test_client, db):
    response = test_client.post("/addimageHandle", data={ "name": "test", "caption": "test", "flag":"True"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].headers["Location"] == "/login"



#Проверяем редактировании картинки
def test_images_edit(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    assert response.status_code == 200
    response = test_client.post("/editImageHandle/1", data={ "name": "test", "caption": "test"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].headers["Location"] == "/"

# Проверяем редактировании несуществующей картинки
def test_images_edit_dont_exist(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    assert response.status_code == 200
    response = test_client.post("/editImageHandle/0", data={ "name": "test", "caption": "test"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].headers["Location"] == "/"

# Проверяем редактировании чужой картинки
def test_images_edit_another_user(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    assert response.status_code == 200
    response = test_client.post("/editImageHandle/8", data={ "name": "test", "caption": "test"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].headers["Location"] == "/"

# Проверяем редактировании без авторизации
def test_images_edit_without_login(test_client):
    response = test_client.post("/editImageHandle/8", data={ "name": "test", "caption": "test"}, follow_redirects = True)
    assert response.status_code == 200
    assert response.history[0].headers["Location"] == "/login"



# Проверка установления страниц
def test_set_page(test_client):
    assert login(test_client).status_code == 200
    response = test_client.get('/setpage/1')
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

# Проверка установления страниц без авторизации
def test_set_page_without_login(test_client):
    response = test_client.get('/setpage/1')
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


# Тестирование интерфейса пользователя

# Проверяем страницу авторизации
def test_login_page(test_client):  
    response = test_client.get('/login')  
    assert response.status_code == 200
    assert b"<h1>Album for you</h1>" in response.data
    assert b'<form name="authorized" action="/loginHandle" method="post">' in response.data
    assert b'<a href="#" class="password-control" onclick="return show_hide_password(this);"><img id="img" src="../static/icons/view.png"/></a>' in response.data

# Проверяем страницу регистрации
def test_register_page(test_client):
    response = test_client.get('/register')
    assert response.status_code == 200
    assert b"<h1>Registration</h1>" in response.data
    assert b'<form name="registred" action="/registerHandle" method="post">' in response.data
    assert b'<p>Already registered?</p>' in response.data

# Проверяем домашную страницу
def test_get_main_page(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    assert response.status_code == 200
    assert b'<div class="AddImage"><a href ="./addimage">Add Image</a></div>' in response.data
    assert b'<div class="Logout"><a href ="./logoutHandle">Logout</a></div>' in response.data
    assert b'<div class="imagesWrapper">' in response.data
    assert b'<div class="navBar">' in response.data

# Проверяем домашную страницу
def test_get_add_image_page(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    assert response.status_code == 200
    response = test_client.get('/addimage')
    assert response.status_code == 200
    assert b'<form method="post" action="/addimageHandle" enctype ="multipart/form-data" >' in response.data
    assert b'<img src="../static/icons/placeholder.png">' in response.data
    assert b'<input type="text" id="name" name="name" placeholder="Name" required>' in response.data
    assert b'<input type="text" id="caption" placeholder="Caption" name="caption">' in response.data
    assert b'<input type="file" id="imagefile" name="imagefile" accept="image/*"  onchange="previewFile()" required>' in response.data

# Проверяем домашную страницу
def test_get_edit_image_page(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    assert response.status_code == 200
    response = test_client.get('/editimage/2')
    assert response.status_code == 200
    assert b'<p>ID : 2</p>' in response.data
    assert b'<img src="/static/upload/admin/27_04_24_02_14_28_672354_faefc69025264e0ef2babbed3d447622c1a2596258816ffec020413577000fec">' in response.data
    assert b'<form method="post" action="/editimageHandle/2" enctype ="multipart/form-data" >' in response.data
    assert b'<input class="buttonDelete" type="button" name="delete" value="Delete" onClick="window.myDialog.showModal()" /></div>' in response.data
    assert b'<dialog id="myDialog">' in response.data


# Тестирование моделей

# Проверяем Select существующего пользователя
def test_users_select(db_test):
    assert db_test["users"].Select("admin") == ('admin', '4903007555c2ab7a850fbb038c379e0cb4d717e569630bfca8917a8d9f11d7c0')

# Проверяем Select несуществующего пользователя
def test_users_select(db_test):
    assert db_test["users"].Select("123") == None

# Проверяем CheckUser
def test_users_select(db_test):
    assert db_test["users"].CheckUser("123") == False
    assert db_test["users"].CheckUser("admin") == True

# Проверяем вставку пользователя
def test_users_insert(db_test):
    db_test["users"].Insert("test", "test")
    assert db_test["users"].Select("test") == ('test', 'test')

# Проверяем удаление cуществующего пользователя
def test_users_delete(db_test):
    assert db_test["users"].CheckUser("test") == True
    db_test["users"].Delete("test")
    assert db_test["users"].CheckUser("test") == False

# Проверяем SelectByLogin
def test_images_select_by_login(db_test):
    assert len(db_test["images"].SelectByLogin("admin")) == 2
    assert db_test["images"].SelectByLogin("admin") == [[1, 'test1', 'test1', 'test1'],[2, 'test2', 'test2', 'test2']]

# Проверяем SelectById
def test_images_select_by_id(db_test):
    assert len(db_test["images"].SelectById(2)) == 1
    assert db_test["images"].SelectById(2) == [[2, 'test2', 'test2', 'test2']]

# Проверяем CheckAuthor
def test_images_check_author(db_test):
    assert db_test["images"].CheckAuthor(2, "admin") == True
    assert db_test["images"].CheckAuthor(2, "123") == False

# Проверяем Insert и Delete
def test_images_insert(db_test):
    result = db_test["images"].Insert("test3", "test3", "test3", "test3")
    assert len(db_test["images"].SelectByLogin("admin")) == 2
    assert len(db_test["images"].SelectByLogin("test3")) == 1
    db_test["images"].Delete(result[0])
    assert len(db_test["images"].SelectByLogin("test3")) == 0

# Проверяем DeleteByUser
def test_images_deleteByUser(db_test):
    db_test["images"].Insert("test3", "test3", "test3", "test3")
    db_test["images"].Insert("test3", "test3", "test3", "test3")
    db_test["images"].Insert("test3", "test3", "test3", "test3")
    assert len(db_test["images"].SelectByLogin("test3")) == 3
    db_test["images"].DeleteByUser("test3")
    assert len(db_test["images"].SelectByLogin("test3")) == 0



# Дополнительные тесты

# Проверяем несуществующий адрес без авторизации
def test_get_not_exist_route_without_login(test_client):
    response = test_client.get('/asdasd')
    assert response.status_code == 302
    assert response.headers['Location'] == "/login"

# Проверяем несуществующий адрес c авторизацией
def test_get_not_exist_route_with_login(test_client):
    response = test_client.post("/loginHandle", data={ "login": "admin", "password": "admin1"}, follow_redirects = True)
    response = test_client.get('/asdasd')
    assert response.status_code == 302
    assert response.headers['Location'] == "/"

