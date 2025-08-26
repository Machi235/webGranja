from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="granjaa"
    )
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def formulario():
    mensaje = ""
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        conn = get_connection()
        cur = conn.cursor()
        sql = "SELECT * FROM usuarios WHERE nombre = %s AND contraseña = %s"
        cur.execute(sql, (usuario, password))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return redirect(url_for("bienvenida", usuario=usuario))
        else:
            mensaje = "Usuario o contraseña incorrectos."

    return render_template("main.html", mensaje=mensaje)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form.get("nombre")
        password = request.form.get("password")
        rol = request.form.get("rol")
        apellido = request.form.get("apellido")
        documento = request.form.get("documento")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")


        conn = get_connection()
        cur = conn.cursor()

        sql = """
        INSERT INTO usuarios 
        (nombre, contraseña, rol, apellido, documento, telefono, correo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (nombre, password, rol, apellido, documento, telefono, correo)
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()

        mensaje = "✅ Usuario registrado con éxito. Ahora puedes iniciar sesión."
        return redirect(url_for("formulario"))

    return render_template("registro.html", mensaje=mensaje)


@app.route("/bienvenida")
def bienvenida():
    usuario = request.args.get("usuario")
    return render_template("inicio.html", usuario=usuario)

@app.route("/registro_animal", methods=["GET", "POST"])
def registro_animal():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form["nombre"]
        especie = request.form["especie"]
        estadoSalud = request.form["estadoSalud"]
        edad = request.form["edad"]
        fechaNacimiento = request.form["fechaNacimiento"]
        fechaLlegada = request.form["fechaLlegada"]
        habitat = request.form["habitat"]
        observaciones = request.form["observaciones"]
        sexo = request.form["sexo"]
        comportamiento = request.form["comportamiento"]

        conn = get_connection()
        cur = conn.cursor()
        sql = """
        INSERT INTO animal 
        (nombre, especie, estadoSalud, edad, fechaNacimiento, fechaLlegada, habitat, observaciones, sexo, comportamiento)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (nombre, especie, estadoSalud, edad, fechaNacimiento, fechaLlegada, habitat, observaciones, sexo, comportamiento)
        cur.execute(sql, valores)
        conn.commit()
        cur.close()
        conn.close()


        mensaje = "✅ Animal registrado con éxito."
        return redirect(url_for("registro_animal"))  # después de registrar vuelve al inicio o donde quieras

    return render_template("cAnimal.html", mensaje=mensaje)

if __name__ == "__main__":
    app.run(debug=True)
