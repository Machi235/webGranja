from flask import Blueprint, flash, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Message

auth = Blueprint("auth", __name__)


# ---------------- LOGIN ----------------
@auth.route("/login", methods=["GET", "POST"])
def formulario():
    mensaje = ""
    if request.method == "POST":
        correo = request.form.get("usuario")
        password = request.form.get("password")

        if not correo or not password:
            mensaje = "Por favor, completa todos los campos."
            return render_template("login.html", mensaje=mensaje)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT idUsuario, contraseña, rol FROM usuarios WHERE correo = %s LIMIT 1", (correo,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and check_password_hash(result["contraseña"], password):
            session["idUsuario"] = result["idUsuario"]
            session["rol"] = result["rol"]
            return redirect(url_for("main.bienvenida"))
        else:
            mensaje = "Usuario o contraseña incorrectos."

    return render_template("login.html", mensaje=mensaje)


# ---------------- REGISTRO ----------------
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

        if not mensaje_usuario and not mensaje_correo:
            cur.execute("""
                INSERT INTO usuarios
                (nombre, contraseña, rol, apellido, documento, telefono, correo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, hashed_password, rol, apellido, documento, telefono, correo))
            conn.commit()

        cur.close()
        conn.close()

        if not mensaje_usuario and not mensaje_correo:
            return redirect(url_for("auth.formulario"))

    # -------- Notificaciones RRHH (para navRrhh.html) --------
    notificaciones_no_leidas = 0
    notificaciones = []
    if 'idUsuario' in session:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM notificacion
            WHERE idUsuario = %s
        """, (session['idUsuario'],))
        notificaciones = cur.fetchall()
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))
        cur.close()
        conn.close()

    return render_template(
        "registro.html",
        mensaje_usuario=mensaje_usuario,
        mensaje_correo=mensaje_correo,
        rol=session.get("rol"),
        notificaciones_no_leidas=notificaciones_no_leidas,
        notificaciones=notificaciones
    )




# ---------------- RECUPERAR CONTRASEÑA ----------------
@auth.route("/recuperar", methods=["GET", "POST"])
def recuperar_password():
    mensaje = ""
    if request.method == "POST":
        correo = request.form.get("correo")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            from flask import current_app
            s = URLSafeTimedSerializer(current_app.secret_key)

            token = s.dumps(correo, salt='recuperar-password')
            link = url_for('auth.restablecer_password_token', token=token, _external=True)

            # Enviar correo
            msg = Message(
                subject="Restablecer tu contraseña - Granja Machis",
                recipients=[correo],
                body=f"Hola,\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n{link}\n\nSi no solicitaste este cambio, ignora este mensaje."
            )

            try:
   
                from servidor import mail
                with current_app.app_context():
                    mail.send(msg)
                mensaje = "Se ha enviado un correo con las instrucciones para restablecer tu contraseña."
            except Exception as e:
                print("Error al enviar correo:", e)
                mensaje = "Error al enviar el correo. Verifica tu conexión o configuración de Gmail."

        else:
            mensaje = "El correo no está registrado."

    return render_template("recuperar.html", mensaje=mensaje)


# ---------------- RESTABLECER CONTRASEÑA ----------------
@auth.route("/restablecer_token/<token>", methods=["GET", "POST"])
def restablecer_password_token(token):
    from flask import current_app
    s = URLSafeTimedSerializer(current_app.secret_key)


    try:
        correo = s.loads(token, salt='recuperar-password', max_age=3600)
    except SignatureExpired:
        return "El enlace ha expirado. Vuelve a solicitar la recuperación.", 400
    except BadSignature:
        return "El enlace no es válido.", 400

    if request.method == "POST":
        nueva_password = request.form.get("password")
        hashed_password = generate_password_hash(nueva_password)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET contraseña = %s WHERE correo = %s", (hashed_password, correo))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("auth.formulario"))

    return render_template("restablecer.html", correo=correo)


# ---------------- VER USUARIOS ----------------
@auth.route("/ver_usuarios", methods=["GET"])
def ver_usuarios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo FROM usuarios WHERE activo = 1 ORDER BY nombre")
    usuarios = cur.fetchall()
    cur.execute("SELECT DISTINCT rol FROM usuarios")
    roles = [row['rol'] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template("verUsuario.html", usuarios=usuarios, roles=roles)

# ---------------- VER USUARIO ----------------
@auth.route("/detalle_usuario/<int:idUsuario>")
def ver_usuario(idUsuario):
    """Muestra la informacion completa de un solo usuario"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo
        FROM usuarios
        WHERE idUsuario = %s
    """,(idUsuario,)) 
    usuario = cur.fetchone()

    cur.close()
    conn.close()

    if not usuario:
        return "usuario no encontrado", 404
    return render_template("detalleUsuario.html", usuario=usuario)

# ---------------- EDITAR USUARIO ----------------
@auth.route("/editar_usuario/<int:idUsuario>", methods=["GET"])
def editar_usuario(idUsuario):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo
        FROM usuarios
        WHERE idUsuario = %s
    """,(idUsuario,)) 
    usuario = cur.fetchone()

    cur.close()
    conn.close()

    if not usuario:
        return "usuario no encontrado", 404
    return render_template("editarUsuario.html", usuario=usuario)

# ---------------- ACTUALIZAR USUARIO ----------------
@auth.route("/actualizar_usuario/<int:idUsuario>", methods=["POST"])
def actualizar_usuario(idUsuario):
    nombre = request.form["nombre"]
    rol = request.form["rol"]
    apellido = request.form["apellido"]
    documento = request.form["documento"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]

    if not all([nombre, rol, apellido, documento, telefono, correo]):
        flash("Todos los campos son obligatorios")
        return redirect(url_for("auth.ver_usuarios"))

    conn = get_connection()
    cur=conn.cursor()

    cur.execute(""" UPDATE usuarios SET nombre=%s, rol=%s, apellido=%s, documento=%s, telefono=%s, correo=%s WHERE idUsuario=%s """,
    (nombre,rol,apellido,documento,telefono,correo, idUsuario))


    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("auth.ver_usuario",idUsuario=idUsuario))

# ---------------- ELIMINAR USUARIO ----------------
@auth.route("/eliminar_usuario/<int:idUsuario>", methods=["POST"])
def eliminar_usuario(idUsuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET activo = 0 WHERE idUsuario=%s",(idUsuario,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("auth.ver_usuarios"))

# ---------------- LOGOUT ----------------
@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.formulario"))
