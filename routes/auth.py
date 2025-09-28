from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection

auth = Blueprint("auth", __name__)  # Recuerda registrarlo con url_prefix si quieres


from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from db import get_connection

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def formulario():
    mensaje = ""
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        #verificamos campos vacios
        if not usuario or not password:
            mensaje="Por favor, completar todos los campos"
            return render_template("login.html", mensaje=mensaje)

        conn = get_connection()
        cur = conn.cursor()
        # Traemos contraseña y rol
        cur.execute("SELECT contraseña, rol FROM usuarios WHERE correo = %s LIMIT 1", (usuario,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and check_password_hash(result[0], password):
            # Guardamos en sesión
            session["usuario"] = usuario
            session["rol"] = result[1]
            return redirect(url_for("main.bienvenida"))  # Redirige a bienvenida según rol
        else:
            mensaje = "Usuario o contraseña incorrectos."

    return render_template("login.html", mensaje=mensaje)


@auth.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje_usuario = ""
    mensaje_correo = ""

    if request.method == "POST":
        nombre = request.form.get("nombre")
        password = request.form.get("password")
        rol = request.form.get("rol")
        apellido = request.form.get("apellido")
        documento = request.form.get("documento")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")
        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Verificar duplicados de usuario y correo
        cur.execute("""
            SELECT nombre, correo
            FROM usuarios
            WHERE nombre = %s OR correo = %s
        """, (nombre, correo))

        resultados = cur.fetchall()
        for r in resultados:
            if r['nombre'] == nombre:
                mensaje_usuario = "Este nombre de usuario ya está registrado."
            if r['correo'] == correo:
                mensaje_correo = "Este correo ya está registrado."

        # Insertar solo si no hay duplicados
        if not mensaje_usuario and not mensaje_correo:
            cur.execute("""
                INSERT INTO usuarios
                (nombre, contraseña, rol, apellido, documento, telefono, correo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, hashed_password, rol, apellido, documento, telefono, correo))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for("auth.formulario"))

        cur.close()
        conn.close()

    return render_template(
        "registro.html",
        mensaje_usuario=mensaje_usuario,
        mensaje_correo=mensaje_correo
    )

@auth.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    mensaje = ""
    if request.method == "POST":
        correo = request.form.get("correo")

        conn = get_connection()
        cur = conn.cursor()
        sql = "SELECT * FROM usuarios WHERE correo = %s"
        cur.execute(sql, (correo,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return redirect(url_for("auth.restablecer_password", correo=correo))
        else:
            mensaje = "El correo no está registrado."

    return render_template("recuperar.html", mensaje=mensaje)

@auth.route("/restablecer/<correo>", methods=["GET", "POST"])
def restablecer_password(correo):
    if request.method == "POST":
        nueva_password = request.form.get("password")
        hashed_password = generate_password_hash(nueva_password)

        conn = get_connection()
        cur = conn.cursor()
        sql = "UPDATE usuarios SET contraseña = %s WHERE correo = %s"
        cur.execute(sql, (hashed_password, correo))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("auth.formulario"))

    return render_template("restablecer.html", correo=correo)


@auth.route("/ver_usuarios", methods=["GET"])
def ver_usuarios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Traer todos los usuarios
    cur.execute("""
        SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo
        FROM usuarios
        ORDER BY nombre
    """)
    usuarios = cur.fetchall()

    # Traer roles distintos para filtro
    cur.execute("SELECT DISTINCT rol FROM usuarios")
    roles = [row['rol'] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return render_template("verUsuario.html", usuarios=usuarios, roles=roles)


@auth.route("/logout")
def logout():
    # Eliminar todas las variables de la sesión
    session.clear()
    # Redirigir al formulario de login
    return redirect(url_for("auth.formulario"))
