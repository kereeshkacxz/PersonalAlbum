import sqlalchemy as sa
dblogin = "kereeshka"
dbpassword = "2580"

class Users_test:
    def __init__(self):

        self.engine = sa.create_engine('mysql+pymysql://'+dblogin+':'+dbpassword+'@localhost/testing')
        self.metaData= sa.MetaData()
        self.metaData.reflect(bind=self.engine)
        self.connection = self.engine.connect()
        self.users = sa.Table("users", self.metaData, autoload_with=self.engine)

    def Select(self, login):
        selectQuery = self.users.select().where(self.users.columns.login == login)
        result = self.connection.execute(selectQuery)
        return result.one_or_none()
    
    def Insert(self, login, password):
        insertQuery = self.users.insert().values(login = login, password = password)
        self.connection.execute(insertQuery)
        self.connection.commit()

    def CheckUser(self, login):
        selectQuery = self.users.select().where(self.users.columns.login == login)
        result = self.connection.execute(selectQuery)
        if result.one_or_none():
            return True
        return False
    
    def Delete(self, login):
        deleteQuery = self.users.delete().where(self.users.columns.login == login)
        self.connection.execute(deleteQuery)
        self.connection.commit()
        

class Images_test:
    def __init__(self):
        self.engine = sa.create_engine('mysql+pymysql://'+dblogin+':'+dbpassword+'@localhost/testing')
        self.metaData= sa.MetaData()
        self.metaData.reflect(bind=self.engine)
        self.connection = self.engine.connect()
        self.images = sa.Table("images", self.metaData, autoload_with=self.engine)
        
    def SelectByLogin(self, login):
        selectQuery = self.images.select().where(self.images.columns.user == login)
        result = self.connection.execute(selectQuery)
        images = []
        for row in result:
            images.append([row.id, row.name, row.caption, row.filename])
        return images
    
    def SelectById(self, id):
        selectQuery = self.images.select().where(self.images.columns.id == id)
        result = self.connection.execute(selectQuery)
        images = []
        for row in result:
            images.append([row.id, row.name, row.caption, row.filename])
        return images

    def CheckAuthor(self,id, login):
        selectQuery = self.images.select().where(self.images.columns.id == id)
        result = self.connection.execute(selectQuery)
        images = []
        for row in result:
            if login != row.user:
                return False
        return True

    def Insert(self, name, caption, user, filename):
        insertQuery = self.images.insert().values(name = name, caption = caption, user = user, filename = filename)
        result = self.connection.execute(insertQuery)
        self.connection.commit()
        return result.inserted_primary_key

    def Update(self, id, newname, newcaption):
        updateQuery = self.images.update().where(self.images.columns.id == id).values(name = newname, caption = newcaption)
        self.connection.execute(updateQuery)
        self.connection.commit()
        

    def Delete(self, id):
        select = self.images.select().where(self.images.columns.id == id)
        result = self.connection.execute(select)
        images = []
        for row in result:
            images.append([row.id, row.name, row.caption, row.filename])
        if len(images) != 1:
            return None
        deleteQuery = self.images.delete().where(self.images.columns.id == id)
        self.connection.execute(deleteQuery)
        self.connection.commit()
        return images[0]

    def DeleteByUser(self, user):
        deleteQuery = self.images.delete().where(self.images.columns.user == user)
        self.connection.execute(deleteQuery)
        self.connection.commit()

    def TakeMaxIndex(self):
        result = self.connection.execute(sa.text("SELECT * FROM images WHERE ID = (SELECT MAX(ID) FROM images)"))
        res = None
        for i in result:
            res = i
        if res:
            return res[0]
        return 0

    def __str__(self):
        connection = self.engine.connect()
        result = connection.execute(sa.text("SELECT * FROM images;"))
        ans = ""
        for i,e in enumerate(result):
            ans += str(i) +' -> ' + str(e) + "\n"
        return ans
    