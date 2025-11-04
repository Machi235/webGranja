from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection

habitat_bp = Blueprint("habitat_bp", __name__)

@habitat_bp.route("/crear_habitat", methods=["GET", "POST"])
def crear_habitat():
    if request.method == "POST":
        try:
            nombre = request.form.get("nombreHabitat")
            min_temp = request.form.get("minTemperatura")
            max_temp = request.form.get("maxTemperatura")
            estado = request.form.get("estado")
            humedad = request.form.get("humedad")
            tipo = request.form.get("tipo")
            tamaño = request.form.get("tamaño")
            capacidad = request.form.get("capacidad")

            if not nombre or not estado or not tipo or not capacidad:
                flash("Faltan campos obligatorios", "error")
                return redirect(url_for("habitat_bp.crear_habitat"))

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO habitat 
                (nombreHabitat, maxTemperatura, estado, humedad, ubicacion, tipo, tamaño, capacidad, minTemperatura)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, max_temp, estado, humedad, "Sin ubicación", tipo, tamaño, capacidad, min_temp))

            conn.commit()
            cur.close()
            conn.close()

            flash("Hábitat registrado con éxito", "success")
            return redirect(url_for("habitat_bp.crear_habitat"))

        except Exception as e:
            flash(f"Error al registrar hábitat: {e}", "error")
            return redirect(url_for("habitat_bp.crear_habitat"))

    # GET
    rol_usuario = session.get("rol", "cuidador")
    notificaciones_no_leidas = 0  # Siempre definido para no romper el nav

    return render_template(
        "habitat.html",
        rol_usuario=rol_usuario,
        notificaciones_no_leidas=notificaciones_no_leidas
    )

@habitat_bp.route("/ver_habitats", methods=["GET"])
def ver_habitats():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT idHabitat, nombreHabitat, maxTemperatura, estado, humedad, ubicacion, tipo, tamaño, capacidad, minTemperatura
        FROM habitat
        WHERE activo = 1
        ORDER BY nombreHabitat
    """)
    habitats = cur.fetchall()

    cur.execute("SELECT DISTINCT estado FROM habitat WHERE activo = 1")
    estados = [row['estado'] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT tipo FROM habitat WHERE activo = 1")
    tipos = [row['tipo'] for row in cur.fetchall()]

    cur.close()
    conn.close()

    rol_usuario = session.get("rol", "cuidador")
    notificaciones_no_leidas = 0

    return render_template(
        "verHabitat.html",
        habitats=habitats,
        estados=estados,
        tipos=tipos,
        rol_usuario=rol_usuario,
        notificaciones_no_leidas=notificaciones_no_leidas
    )
