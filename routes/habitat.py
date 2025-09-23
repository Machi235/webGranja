from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

habitat_bp = Blueprint("habitat_bp", __name__)

@habitat_bp.route("/crear_habitat", methods=["GET", "POST"])
def crear_habitat():
    if request.method == "POST":
        try:
            # Obtener datos del formulario
            nombre = request.form.get("nombreHabitat")
            min_temp = request.form.get("minTemperatura")
            max_temp = request.form.get("maxTemperatura")
            estado = request.form.get("estado")
            humedad = request.form.get("humedad")
            tipo = request.form.get("tipo")
            tamaño = request.form.get("tamaño")
            capacidad = request.form.get("capacidad")

            # Validación backend (seguridad extra)
            if not nombre or not estado or not tipo or not capacidad:
                flash("❌ Faltan campos obligatorios", "error")
                return redirect(url_for("habitat_bp.crear_habitat"))

            # Formatear temperatura
            temperatura = f"{min_temp}-{max_temp}" if min_temp and max_temp else None

            # Guardar en la base de datos
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO habitat 
                (nombreHabitat, temperatura, estado, humedad, ubicacion, tipo, tamaño, capacidad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, temperatura, estado, humedad, "Sin ubicación", tipo, tamaño, capacidad))

            conn.commit()
            cur.close()
            conn.close()

            flash("✅ Hábitat registrado con éxito", "success")
            return redirect(url_for("habitat_bp.crear_habitat"))

        except Exception as e:
            flash(f"❌ Error al registrar hábitat: {e}", "error")
            return redirect(url_for("habitat_bp.crear_habitat"))

    return render_template("habitat.html")
