from flask import Blueprint, flash, make_response, render_template, request, redirect, url_for, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_mail import Message
from werkzeug.utils import secure_filename
import os
from io import BytesIO #Modulo de entradas y salidas
from reportlab.lib.pagesizes import letter #tamaño de papel
from reportlab.lib.styles import getSampleStyleSheet #Estilos de texto
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image #Contenido de pdf
from reportlab.lib.units import cm #Usar unidades de medida 


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

    # Inicializamos variables
    nombre = ""
    password = ""
    rol = ""
    apellido = ""
    documento = ""
    telefono = ""
    correo = ""
    hashed_password = ""
    nombre_archivo = None

    if request.method == "POST":
        nombre = request.form.get("nombre")
        password = request.form.get("password")
        rol = request.form.get("rol")
        apellido = request.form.get("apellido")
        documento = request.form.get("documento")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")
        hashed_password = generate_password_hash(password)

        # ------------------ Validación usuario y correo ------------------
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

        # ------------------ Manejo de archivo y registro ------------------
        if not mensaje_usuario and not mensaje_correo:
            # Subir foto solo si existe
            foto_file = request.files.get("foto")
            if foto_file and foto_file.filename != "":
                filename = secure_filename(foto_file.filename)
                upload_folder = os.path.join(current_app.root_path, "static/uploads/usuarios")
                os.makedirs(upload_folder, exist_ok=True)  # Crear carpeta si no existe
                foto_file.save(os.path.join(upload_folder, filename))
                nombre_archivo = f"uploads/usuarios/{filename}"  # Ruta relativa para DB

            # Insertar usuario
            cur.execute("""
                INSERT INTO usuarios
                (nombre, contraseña, rol, apellido, documento, telefono, correo, foto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, hashed_password, rol, apellido, documento, telefono, correo, nombre_archivo))

            nuevo_id_usuario = cur.lastrowid

            # ------------------ Notificaciones a Admin y RRHH ------------------
            cur.execute("SELECT idUsuario FROM usuarios WHERE rol IN ('Admin', 'RRHH') AND activo = 1")
            destinatarios = cur.fetchall()

            from datetime import datetime
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            titulo = "Nuevo usuario registrado"
            descripcion = f"Se ha registrado el usuario {nombre} ({rol})."

            for d in destinatarios:
                cur.execute("""
                    INSERT INTO notificacion (idUsuario, titulo, descripcion, fecha, leida)
                    VALUES (%s, %s, %s, %s, 0)
                """, (d['idUsuario'], titulo, descripcion, fecha_actual))

            conn.commit()
            cur.close()
            conn.close()

            return redirect(url_for("auth.formulario"))

        # Cerrar conexión si hubo errores de usuario/correo
        cur.close()
        conn.close()

    # -------- Notificaciones para nav por roles --------
    rol_usuario = session.get("rol")
    id_usuario = session.get("idUsuario")
    notificaciones_no_leidas = 0
    notificaciones = []

    if id_usuario:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (id_usuario,))
        notificaciones = cur.fetchall()
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))
        cur.close()
        conn.close()

    return render_template(
        "registro.html",
        mensaje_usuario=mensaje_usuario,
        mensaje_correo=mensaje_correo,
        rol=rol_usuario,
        notificaciones=notificaciones,
        notificaciones_no_leidas=notificaciones_no_leidas
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
    cur.execute("""
        SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo, foto
        FROM usuarios
        WHERE activo = 1
        ORDER BY nombre
    """)
    usuarios = cur.fetchall()

    cur.execute("SELECT DISTINCT rol FROM usuarios")
    roles = [row['rol'] for row in cur.fetchall()]
    cur.close()
    conn.close()

    # Información para nav por roles
    rol_usuario = session.get("rol")
    id_usuario = session.get("idUsuario")
    notificaciones_no_leidas = 0
    notificaciones = []

    if id_usuario:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (id_usuario,))
        notificaciones = cur.fetchall()
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))
        cur.close()
        conn.close()

    return render_template(
        "verUsuario.html",
        usuarios=usuarios,
        roles=roles,
        rol=rol_usuario,
        notificaciones=notificaciones,
        notificaciones_no_leidas=notificaciones_no_leidas
    )


# ---------------- VER DETALLE DE USUARIO ----------------
@auth.route("/detalle_usuario/<int:idUsuario>", methods=["GET"])
def ver_usuario(idUsuario):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo, foto
        FROM usuarios
        WHERE idUsuario = %s
    """, (idUsuario,))
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if not usuario:
        return "Usuario no encontrado", 404

    # Información para nav
    rol_usuario = session.get("rol")
    id_usuario_sesion = session.get("idUsuario")
    notificaciones_no_leidas = 0
    notificaciones = []

    if id_usuario_sesion:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (id_usuario_sesion,))
        notificaciones = cur.fetchall()
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))
        cur.close()
        conn.close()

    return render_template(
        "detalleUsuario.html",
        usuario=usuario,
        rol=rol_usuario,
        notificaciones=notificaciones,
        notificaciones_no_leidas=notificaciones_no_leidas
    )

# ---------------- EDITAR USUARIO (FORMULARIO) ----------------
@auth.route("/editar_usuario/<int:idUsuario>", methods=["GET"])
def editar_usuario(idUsuario):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM usuarios WHERE idUsuario = %s", (idUsuario,))
    usuario = cur.fetchone()

    cur.close()
    conn.close()

    if not usuario:
        flash("Usuario no encontrado")
        return redirect(url_for("auth.ver_usuarios"))

    return render_template("editarUsuario.html", usuario=usuario)

# ---------------- ACTUALIZAR USUARIO ----------------
@auth.route("/actualizar_usuario/<int:idUsuario>", methods=["POST"])
def actualizar_usuario(idUsuario):
    nombre = request.form.get("nombre")
    rol = request.form.get("rol")
    apellido = request.form.get("apellido")
    documento = request.form.get("documento")
    telefono = request.form.get("telefono")
    correo = request.form.get("correo")
    foto = request.files.get("foto")  # Imagen del formulario

    # Validación
    if not all([nombre, rol, apellido, documento, telefono, correo]):
        flash("Todos los campos son obligatorios")
        return redirect(url_for("auth.editar_usuario", idUsuario=idUsuario))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Obtener el usuario actual para conservar la foto si no suben una nueva
    cur.execute("SELECT foto FROM usuarios WHERE idUsuario = %s", (idUsuario,))
    usuario_actual = cur.fetchone()
    imagen_actual = usuario_actual["foto"] if usuario_actual else None

    # Guardar nueva imagen si se envió
    if foto and foto.filename != "":
        filename = secure_filename(foto.filename)
        # Guardamos en la carpeta static/uploads/usuarios
        ruta_carpeta = os.path.join(current_app.root_path, 'static/uploads/usuarios')
        os.makedirs(ruta_carpeta, exist_ok=True)  # Crear carpeta si no existe
        ruta_guardado = os.path.join(ruta_carpeta, filename)
        foto.save(ruta_guardado)
        # Guardar ruta relativa en la BD (para url_for)
        nueva_imagen = f"uploads/usuarios/{filename}"
    else:
        nueva_imagen = imagen_actual  # Mantener la misma imagen

    # Actualizar usuario
    cur.execute("""
        UPDATE usuarios
        SET nombre=%s, rol=%s, apellido=%s, documento=%s, telefono=%s, correo=%s, foto=%s
        WHERE idUsuario=%s
    """, (nombre, rol, apellido, documento, telefono, correo, nueva_imagen, idUsuario))

    conn.commit()
    cur.close()
    conn.close()

    flash("Usuario actualizado correctamente")
    return redirect(url_for("auth.ver_usuario", idUsuario=idUsuario))


# ---------------- ELIMINAR USUARIO ----------------
@auth.route("/eliminar_usuario/<int:idUsuario>", methods=["POST"])
def eliminar_usuario(idUsuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios SET activo = 0 WHERE idUsuario=%s", (idUsuario,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("auth.ver_usuarios"))

@auth.route("/pdf_usuario/<int:idUsuario>")
def generar_pdf(idUsuario):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT u.idUsuario, nombre, apellido, rol, documento, telefono, correo, nombreTurno, foto FROM usuarios AS u LEFT JOIN usuarioturno AS t 
                ON u.idUsuario = t.idUsuario LEFT JOIN horariosturnos AS h ON t.idHorario = h.idHorario  WHERE u.idUsuario = %s """, (idUsuario,))
    usuario = cur.fetchone()

    buffer = BytesIO() #Crea un espacio temporal en memoria
    pdf = SimpleDocTemplate(buffer, pagesize=letter) #Se crea el documento pdf
    elements = [] #Lista vacia donde se pone el contenido
    styles = getSampleStyleSheet() #conjunto de estilos 

    elements.append(Paragraph(f"<b>Ficha del usuario</b>", styles["Title"])) #Agrgar un parrafro al pdf

    ruta_imagen = os.path.join("static", usuario["foto"]) #Une la ruta base con el nombre de la imagen
    img = Image(ruta_imagen, width=8*cm, height=8*cm) #Carga la imagen ajustandolo al tamaño
    img.hAlign = "CENTER" #Ajusta la imagen
    elements.append(img)
    elements.append(Spacer(1, 30))

    contenido = f"""
    <b>Nombre: </b>{usuario['nombre']}<br/>
    <b>Apellido: </b>{usuario['apellido']}<br/>
    <b>Rol: </b>{usuario['rol']}<br/>
    <b>Documento: </b>{usuario['documento']}<br/>
    <b>Telefono: </b>{usuario['telefono']}<br/>
    <b>Correo electronica: </b>{usuario['correo']}<br/>
    <b>Turno asigando: </b>{usuario['nombreTurno']}<br/>"""
    

    styles = getSampleStyleSheet()
    estilo_grande = styles["Normal"].clone('estilo_grande')
    estilo_grande.fontSize = 14   # tamaño de letra
    estilo_grande.leading = 40    # espacio entre líneas

    elements.append(Paragraph(contenido, estilo_grande))


    pdf.build(elements) #Crea el pdf con todos elementos en el mismo orden  

    response = make_response(buffer.getvalue()) # sE crea una respuesta http con los bytes obtenidos en el buffer    
    response.headers["Content-Type"] = "application/pdf" #Dice que el contenido es un pdf
    response.headers["Content-Disposition"] = "inline; filename=animal.pdf" #Lo abre directamente
    return response 



# ---------------- LOGOUT ----------------
@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.formulario"))

