from flask import Blueprint, request, jsonify, redirect, url_for, render_template, current_app
from db import get_connection

notificaciones_bp = Blueprint("notificaciones_bp", __name__)

# Crear notificación
@notificaciones_bp.route("/crear_notificacion", methods=["GET", "POST"])
def crear_notificacion():
    if request.method == "POST":
        titulo = request.form.get("titulo")
        rol = request.form.get("rol")
        descripcion = request.form.get("descripcion")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notificacion (titulo, rol, descripcion) VALUES (%s, %s, %s)",
            (titulo, rol, descripcion)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("notificaciones_bp.crear_notificacion"))

    return render_template("admininicio.html")


@notificaciones_bp.route("/marcar_leida/<int:noti_id>", methods=["POST"])
def marcar_leida(noti_id):
    current_app.logger.info("marcar_leida called: %s, method=%s", noti_id, request.method)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notificacion SET leida = 1 WHERE id = %s", (noti_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True, "id": noti_id})

@notificaciones_bp.route("/panel")
def panel():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)  # 👈 importante

    # Solo traer las no leídas
    cur.execute("SELECT * FROM notificacion WHERE leida = 0 ORDER BY id DESC")
    notificaciones = cur.fetchall()

    # Contador de no leídas
    cur.execute("SELECT COUNT(*) AS total FROM notificacion WHERE leida = 0")
    no_leidas = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return render_template(
        "inicio.html",
        notificaciones=notificaciones,
        notificaciones_no_leidas=no_leidas
    )
