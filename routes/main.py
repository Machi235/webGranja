from flask import Blueprint, render_template, request, session, redirect, url_for
from db import get_connection

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")

@main.route("/bienvenida")
def bienvenida():
    if "idUsuario" not in session or "rol" not in session:
        return redirect(url_for("auth.formulario"))

    id_usuario = session["idUsuario"]
    rol = session["rol"]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Traer datos del usuario
    cur.execute("""
        SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo
        FROM usuarios
        WHERE idUsuario = %s
    """, (id_usuario,))
    usuario = cur.fetchone()

    # Traer notificaciones no leídas según rol
    cur.execute("""
        SELECT id, leida, titulo, descripcion, fecha
        FROM notificacion
        WHERE rol = %s AND leida = 0
        ORDER BY fecha DESC
    """, (rol,))
    notificaciones = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS total FROM notificacion WHERE rol = %s AND leida = 0", (rol,))
    no_leidas = cur.fetchone()["total"]

    cur.close()
    conn.close()

    # Elegir template según rol
    if rol == "Admin":
        template = "admininicio.html"
    elif rol == "Guia":
        template = "inicioGuia.html"
    elif rol == "Cuidador":
        template = "inicio.html"
    else:
        template = "inicio.html"

    return render_template(
        template,
        usuario=usuario,
        rol=rol,
        notificaciones=notificaciones,
        notificaciones_no_leidas=no_leidas
    )

