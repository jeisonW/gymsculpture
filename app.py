import time
from flask_session import Session
from flask import Flask, jsonify, redirect, render_template, request, session
from helper import  login_required
from werkzeug.security import generate_password_hash , check_password_hash
import pyodbc
from celery import Celery
from datetime import datetime, timedelta
import redis



app = Flask(__name__)
app.debug = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


try:##verificar que no haya ningun error al conectarse con la BF
    #esto tienen que cambiarlo en base  a su computadora
    conexion =  pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-F9CVAAQJ\SQLEXPRESS;DATABASE=sculpture_gym;UID=TiendaKD;PWD=1234')
    #conexion = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-DJ008NGO\;DATABASE=Sculpture_gym;Trusted_Connection=yes;')
except:
    print("FAIL")

cursor = conexion.cursor()

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register" ,  methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if request.form.get("password") != request.form.get("passwordConfirmar"):
            return render_template("CrearCuenta.html" , error = "Las contraseñas no coinciden ") # 

        if request.form.get("correo"):
            if not request.form.get("correo").endswith('@gmail.com') and not request.form.get("correo").endswith('@hotmail.com'):#validar que es admitido
                return render_template("CrearCuenta.html" , error = "correo invalido")   
            
        sql = "select correo from usuarios where correo = ?"
        rows = cursor.execute(sql, (request.form.get("correo")))
        rows = cursor.fetchall()

        if len(rows) > 0:
            return render_template("CrearCuenta.html" , error = "usuario previamente registrado") #
         
        if request.form.get("telefono"):# si escribe un telefono se valida que sea numerico y que el tamaño sea ocho
            if not request.form.get("telefono").isnumeric():
                return render_template("CrearCuenta.html" , error = "telefono invalido")
            if len(request.form.get("telefono")) != 8:
                return render_template("CrearCuenta.html" , error = "telefono invalido")
            
        if not request.form.get("telefono"):
            sql="INSERT INTO dbo.usuarios(correo,pass,nombre,estado,puntos) VALUES (?,?,?,'si',0)"
            cursor.execute(sql,  (request.form.get("correo"),generate_password_hash(request.form.get("password")),  request.form.get("nombre")))
            conexion.commit() 
        else:
            sql="INSERT INTO dbo.usuarios(correo,pass,nombre,telefono,estado,puntos) VALUES (?,?,?,?,'si',0)"
            cursor.execute(sql,  (request.form.get("correo"),generate_password_hash(request.form.get("password")),request.form.get("nombre"),request.form.get("telefono"),  ))
            conexion.commit() 
       
        return render_template("login.html" , succes = "usuario instalado correctamente")
    else : 
        return render_template("CrearCuenta.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        correo = request.form.get("correo")
        password = request.form.get("password")

        query = "select * from usuarios where correo = ?"
        rows =cursor.execute(query, (correo))
        rows = cursor.fetchall()
        match = check_password_hash(rows[0][1] , password)

        if int(rows[0][5]) <= 0:
            return render_template("login.html" , error="Puntos insuficientes")

        if len(rows) == 0 :
            return render_template("login.html" , error="Nombre de usuario o contraseña incorrecta")
        else:
            session["user_id"] = rows
            print(session["user_id"][0][3])
            return redirect("/")       
    else : 
        return render_template("login.html")
    
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/user" ,  methods=["GET", "POST"])
@login_required
def user():
    if request.method == "POST":
        sql = "update usuarios set puntos = ?  where correo = ?"
        cursor.execute(sql , (request.form.get("puntos") , request.form.get("correo")))
        cursor.commit()
        return redirect("/user")
    else:
        sql = "select * from usuarios where estado = 'si' and correo != 'munguiak435@gmail.com' and correo != 'crusthianvg98@gmail.com'"
        resultados = cursor.execute(sql)
        resultados = cursor.fetchall()
        return render_template("usuarios.html" , user = resultados)

if __name__ == '__main__':
    app.run()