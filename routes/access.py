from flask import Blueprint, render_template, session
from db import get_connection

access_bp = Blueprint("access_bp", __name__)

@access_bp.route("/accesos")
def accesos():

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # ============================
    #   OBTENER NOTIFICACIONES
    # ============================
    notificaciones_no_leidas = 0
    notificaciones = []

    if 'idUsuario' in session:
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session['idUsuario'],))
        notificaciones = cur.fetchall()
        # Contar solo las no leídas
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))

    cur.close()
    conn.close()

    # ============================
    #   RENDERIZAR TEMPLATE
    # ============================
    return render_template(
        "accesos.html",
        rol=session.get("rol"),
        notificaciones_no_leidas=notificaciones_no_leidas,
        notificaciones=notificaciones
    )
