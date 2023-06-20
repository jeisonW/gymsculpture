from flask_session import Session
from flask import Flask, jsonify, redirect, render_template, request, session
from helper import  login_required
import pyodbc


app = Flask(__name__)
app.debug = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


try:##verificar que no haya ningun error al conectarse con la BF
    #esto tienen que cambiarlo en base  a su computadora
    conexion =  pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=LAPTOP-F9CVAAQJ\SQLEXPRESS;DATABASE=sculpture_gym;UID=TiendaKD;PWD=1234')
except:
    print("FAIL")

cursor = conexion.cursor()

@app.route("/")
@login_required
def index():
    return ""

@app.route("/register" ,  methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if not request.form.get("correo").endswith("@gmail.com"):
            next # correo no valido
        sql = "select correo from usuarios where correo = ?"
        rows = cursor.execute(sql, (request.form.get("correo")))
        rows = cursor.fetchall()

        if len(rows) > 0:
            next # correo ya estaba insertado en la base de datos            

        if request.form.get("password") != request.form.get("confirmacion"):
            return render_template("CrearCuenta.html" , error = "Las contraseñas no coinciden ") # 

        # if request.form.get ("telefono") 
        # validar que sea numero 
        # validar el tamaño correcto 
        # 
        #sql=  "insert into usuarios (correo ,  pass , nombre , telefono ) values (?,?,?,?)"
        #cursor.execute(sql, request.form.get("correo"),  generate_password_hash(request.form.get("password")), request.form.get("nombre"),request.form.get("telefono")))
        #conexion.commit() 
        return redirect("/login")
 
    else : 
        return render_template("CrearCuenta.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
       next     
    else : 
        return render_template("login.html")

if __name__ == '__main__':
    app.run()