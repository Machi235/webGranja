from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection

alimento_bp = Blueprint("alimento_bp", __name__)

@alimento_bp.route("/agregar_alimento", methods=["GET", "POST"])
def agregar_alimento():

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
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))

    # ============================
    #   MÉTODO GET → Mostrar form
    # ============================
    if request.method == "GET":
        cur.close()
        conn.close()
        return render_template(
            "alimento.html",
            rol=session.get("rol"),
            notificaciones_no_leidas=notificaciones_no_leidas,
            notificaciones=notificaciones
        )

    # ============================
    #   MÉTODO POST → Insertar BD
    # ============================

    # Recibir listas del formulario
    origenes = request.form.getlist("origen[]")
    especies = request.form.getlist("idEspecie[]")

    # Validación simple
    if not origenes:
        flash("Debe agregar al menos un alimento.", "danger")
        return redirect(url_for("alimento_bp.agregar_alimento"))

    # Insertar cada alimento
    for origen, especie in zip(origenes, especies):
        if origen.strip() == "":
            continue  # Saltar entradas vacías

        cur.execute("""
            INSERT INTO alimento (origen, idEspecie)
            VALUES (%s, %s)
        """, (origen, especie if especie != "" else None))

    conn.commit()
    cur.close()
    conn.close()

    flash("Alimentos agregados correctamente", "success")
    return redirect(url_for("alimento_bp.agregar_alimento"))
