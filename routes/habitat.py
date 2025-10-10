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
                flash("Faltan campos obligatorios", "error")
                return redirect(url_for("habitat_bp.crear_habitat"))

            # Guardar en la base de datos
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

    return render_template("habitat.html")

@habitat_bp.route("/ver_habiatats", methods=["GET"])
def ver_habitats():
    """Muestra todos los animales registros """
    conn=get_connection()
    cur=conn.cursor(dictionary=True)
    cur.execute(""" SELECT idHabitat, nombreHabitat, maxTemperatura, estado, humedad,  ubicacion, tipo, tamaño, capacidad, minTemperatura FROM habitat WHERE activo = 1 ORDER BY nombreHabitat """)

    habitats = cur.fetchall()

    cur.execute("SELECT DISTINCT estado FROM habitat WHERE activo = 1")
    estados= [row['estado'] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT tipo FROM habitat WHERE activo = 1")
    tipos=[row['tipo'] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template("verHabitat.html", habitats=habitats, estados=estados, tipos=tipos)

@habitat_bp.route("/detalle_habitat/<int:idHabitat>")
def ver_habitat(idHabitat):
    conn=get_connection()
    cur=conn.cursor(dictionary=True)

    cur.execute(""" SELECT idHabitat, nombreHabitat, maxTemperatura, estado, humedad,  ubicacion, tipo, tamaño, capacidad, minTemperatura FROM habitat WHERE idHabitat = %s """,
    (idHabitat,))

    habitat = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("detalleHabitat.html", habitat=habitat)

@habitat_bp.route("/editar_habitat/<int:idHabitat>", methods=["GET"])
def editar_habitat(idHabitat):
    conn=get_connection()
    cur=conn.cursor(dictionary=True)
    cur.execute(""" SELECT idHabitat, nombreHabitat, maxTemperatura, estado, humedad,  ubicacion, tipo, tamaño, capacidad, minTemperatura FROM habitat WHERE idHabitat = %s """,
    (idHabitat,))

    habitat=cur.fetchone()

    cur.close()
    conn.close()

    return render_template("editarHabitat.html",habitat=habitat)

@habitat_bp.route("/actualizar_habitat/<int:idHabitat>", methods=["POST"])
def actualizar_habitat(idHabitat):
    nombre = request.form["nombreHabitat"]
    min_temp = request.form["minTemperatura"]
    max_temp = request.form["maxTemperatura"]
    estado = request.form["estado"]
    humedad = request.form["humedad"]
    tipo = request.form["tipo"]
    tamaño = request.form["tamaño"]
    capacidad = request.form["capacidad"]

    if not all([nombre, min_temp, max_temp, estado, humedad, tipo, tamaño, capacidad ]):
        flash("Todos los campos son obligatorios")
        return redirect(url_for("habitat_bp.ver_habitats"))


    conn = get_connection()
    cur=conn.cursor()

    cur.execute(""" UPDATE habitat SET nombreHabitat=%s, minTemperatura=%s, maxTemperatura=%s, estado=%s, humedad=%s, tipo=%s, tamaño=%s, capacidad=%s WHERE idHabitat=%s""",
    (nombre,min_temp,max_temp,estado,humedad,tipo,tamaño,capacidad, idHabitat))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("habitat_bp.ver_habitat", idHabitat=idHabitat))

@habitat_bp.route("/eliminar_habitat/<int:idHabitat>", methods=["POST"])
def eliminar_habitat(idHabitat):
    conn=get_connection()
    cur=conn.cursor()

    cur.execute("UPDATE habitat SET activo=0 WHERE idHabitat=%s", (idHabitat,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("habitat_bp.ver_habitats")) 
