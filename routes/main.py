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

    # 🔹 Traer datos del usuario
    cur.execute("""
        SELECT idUsuario, nombre, apellido, rol, documento, telefono, correo
        FROM usuarios
        WHERE idUsuario = %s
    """, (id_usuario,))
    usuario = cur.fetchone()

    # 🔔 Traer notificaciones por rol o por usuario
    cur.execute("""
        SELECT id, titulo, descripcion, fecha, leida
        FROM notificacion
        WHERE rol = %s OR idUsuario = %s
        ORDER BY fecha DESC
    """, (rol, id_usuario))
    notificaciones = cur.fetchall()

    # 📬 Contar notificaciones no leídas
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM notificacion
        WHERE (rol = %s OR idUsuario = %s) AND leida = 0
    """, (rol, id_usuario))
    no_leidas = cur.fetchone()["total"]

    # 📊 Datos para gráfica
    cur.execute("SELECT COUNT(idAnimal) as animales, estadoSalud FROM animal GROUP BY estadoSalud")
    estados = cur.fetchall()
    etiquetas = [f"{fila['animales']} animales {fila['estadoSalud']}" for fila in estados] if estados else []
    valores = [fila['animales'] for fila in estados] if estados else []

    cur.close()
    conn.close()

    if rol == "Administrador":
        return render_template(
            "navAdmin.html",
            usuario=usuario,
            rol=rol,
            idUsuario=id_usuario,
            notificaciones=notificaciones,
            notificaciones_no_leidas=no_leidas,
            etiquetas=etiquetas,   # ✅ agregado
            valores=valores        # ✅ agregado
        )
    else:
        return render_template(
            "inicioprueba.html",
            usuario=usuario,
            rol=rol,
            idUsuario=id_usuario,
            notificaciones=notificaciones,
            notificaciones_no_leidas=no_leidas,
            etiquetas=etiquetas,   # ✅ agregado
            valores=valores        # ✅ agregado
        )
