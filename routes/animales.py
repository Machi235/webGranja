import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from db import get_connection

animales = Blueprint("animales", __name__)

# Carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = os.path.join("static", "uploads")

# Crear la carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@animales.route("/registro_animal", methods=["GET", "POST"])
def registro_animal():
    if request.method == "POST":
        try:
            # 1. Datos del formulario
            nombre = request.form.get("nombre")
            especie = request.form.get("especie")
            salud = request.form.get("salud")
            edad = request.form.get("edad")
            nacimiento = request.form.get("fechaNacimiento")
            llegada = request.form.get("fechaLlegada")
            habitat = request.form.get("habitat")
            observaciones = request.form.get("observaciones")
            sexo = request.form.get("sexo")

            # 2. Validación rápida
            if not nombre or not especie or not edad or not salud or not habitat or not observaciones or not sexo:
                return jsonify({"error": "Faltan campos obligatorios"}), 400

            # 3. Guardar imagen
            archivo = request.files.get("imagen")
            filename = None
            if archivo and archivo.filename != "":
                filename = secure_filename(archivo.filename)
                archivo.save(os.path.join(UPLOAD_FOLDER, filename))

            # 4. Guardar en la base de datos
            conn = get_connection()
            cur = conn.cursor()
            sql = """
            INSERT INTO animal 
            (nombre, especie, estadoSalud, edad, fechaNacimiento, fechaLlegada, habitat, observaciones, sexo, imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (nombre, especie, salud, edad, nacimiento, llegada, habitat, observaciones, sexo, filename))
            conn.commit()
            cur.close()
            conn.close()

            return jsonify({"mensaje": "✅ Animal registrado con éxito"}), 200

        except Exception as e:
            print("Error al registrar animal:", str(e))
            return jsonify({"error": "Ocurrió un error en el servidor"}), 500

    # GET: mostrar el formulario
    return render_template("crearAnimal.html")


@animales.route("/ver_animales", methods=["GET"])
def ver_animales():
    """Muestra todos los animales registrados"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Traer todos los animales
    cur.execute("""
        SELECT idAnimal, nombre, especie, estadoSalud, edad, fechaNacimiento, fechaLlegada, habitat, sexo, imagen
        FROM animal
        ORDER BY nombre
    """)
    animales = cur.fetchall()

    # Traer especies y estados de salud para filtros
    cur.execute("SELECT DISTINCT especie FROM animal")
    especies = [row['especie'] for row in cur.fetchall()]

    cur.execute("SELECT DISTINCT estadoSalud FROM animal")
    estados = [row['estadoSalud'] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template("verAnimal.html", animales=animales, especies=especies, estados=estados)
