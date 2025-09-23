from flask import Blueprint, render_template, request, session, redirect, url_for
from db import get_connection

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")

@main.route("/bienvenida")
def bienvenida():
    # 👇 Si no hay sesión, redirigir al login
    if "usuario" not in session or "rol" not in session:
        return redirect(url_for("auth.formulario"))

    usuario = session["usuario"]
    rol = session["rol"]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # 👇 Traer notificaciones no leídas según rol
    cur.execute("""
        SELECT id, leida, titulo, descripcion, fecha
        FROM notificacion
        WHERE rol = %s AND leida = 0
        ORDER BY fecha DESC
    """, (rol,))
    notificaciones = cur.fetchall()

    # 👇 Contar notificaciones no leídas
    cur.execute("SELECT COUNT(*) AS total FROM notificacion WHERE rol = %s AND leida = 0", (rol,))
    no_leidas = cur.fetchone()["total"]

    cur.close()
    conn.close()

    # 👇 Renderizar templates distintos según rol
    if rol == "Admin":
        template = "admininicio.html"
    elif rol == "Guia":
        template = "inicioGuia.html"
    elif rol == "Cuidador":
        template = "inicio.html"
    else:
        template = "inicio.html"  # fallback

    return render_template(
        template,
        usuario=usuario,
        rol=rol,
        notificaciones=notificaciones,
        notificaciones_no_leidas=no_leidas
    )
