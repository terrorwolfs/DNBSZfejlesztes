from WebApp import app
from flask import render_template

class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        
    def get_email(self):
        return self.email



@app.route("/index")
@app.route("/")
def index():
    page = "Python 3.13"
    
    user = {
              "login" : "John",
              "password" : "qweasd"
            }
    
    posts = [
               {
                   
                    "author": User("John", "john@uni-pannon.hu"),
                    "body" :  "lkdsfnlksdnflknsw jwsenflsknc"
               },
               {
                    "author": User("Bob","bob@uni-pannon.hu"),
                    "body" :  "qweqweqweqweqweqweqweqweqweqwe"
               },
               {
                    "author": User("Kevin","kevin@uni-pannon.hu"),
                    "body" :  "bnmbnmbnmbnmbnmbnmbnmbnmbnmbnmb"
               }
             
            ]
    return render_template(
        'index.html',
        page_title = page,
        user = user, posts = posts)
    

@app.route("/login")
def login():
    page = "Python 3.13"
    
    user = {
              "login" : "John",
              "password" : "qweasd"
            }
    return render_template("login.html", user = user)
