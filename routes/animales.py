import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify,  make_response
from werkzeug.utils import secure_filename
from db import get_connection
import pdfkit

animales = Blueprint("animales", __name__)

# Carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = os.path.join("static", "uploads")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@animales.route("/registro_animal", methods=["GET", "POST"])
def registro_animal():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

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

            # 2. Validación de campos obligatorios
            if not nombre or not especie or not salud or not edad or not habitat or not sexo:
                return jsonify({"error": "Faltan campos obligatorios"}), 400

            # 3. Validar especie
            cur.execute("SELECT COUNT(*) AS total FROM especie WHERE idEspecie = %s", (especie,))
            result = cur.fetchone()
            if result['total'] == 0:
                return jsonify({"error": "La especie seleccionada no existe en la base de datos"}), 400

            # 4. Validar hábitat
            cur.execute("SELECT COUNT(*) AS total FROM habitat WHERE idHabitat = %s", (habitat,))
            result = cur.fetchone()
            if result['total'] == 0:
                return jsonify({"error": "El hábitat seleccionado no existe en la base de datos"}), 400

            # 5. Guardar imagen
            archivo = request.files.get("imagen")
            filename = None
            if archivo and archivo.filename != "":
                filename = secure_filename(archivo.filename)
                archivo.save(os.path.join(UPLOAD_FOLDER, filename))

            # 6. Guardar el animal en la base de datos
            sql = """
            INSERT INTO animal 
            (nombre, especie, estadoSalud, edad, fechaNacimiento, fechaLlegada, habitat, observaciones, sexo, imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (nombre, especie, salud, edad, nacimiento, llegada, habitat, observaciones, sexo, filename))
            conn.commit()

            return jsonify({"mensaje": "✅ Animal registrado con éxito"}), 200

        except Exception as e:
            print("Error al registrar animal:", str(e))
            return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

    # === GET: cargar especies y hábitats desde la BD ===
    cur.execute("SELECT idEspecie, tipoEspecie FROM especie ORDER BY tipoEspecie")
    especies = cur.fetchall()

    cur.execute("SELECT idHabitat, nombreHabitat FROM habitat ORDER BY nombreHabitat")
    habitats = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("crearAnimal.html", especies=especies, habitats=habitats)

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

@animales.route("/detalle_animal/<int:idAnimal>")
def ver_animal(idAnimal):
    """Muestra la informacion completa de un solo animal"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT idAnimal, nombre, especie, estadoSalud, edad, fechaNacimiento, fechaLlegada, habitat, observaciones, sexo, imagen
        FROM animal
        WHERE idAnimal = %s
    """,(idAnimal,)) 
    animal = cur.fetchone()

    cur.close()
    conn.close()

    if not animal:
        return "Animal no encontrado", 404
    return render_template("detalleAnimal.html", animal=animal)

@animales.route("/pdf_animal/<int:idAnimal>")
def generar_pdf(idAnimal):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT idAnimal, nombre, especie, estadoSalud, edad, fechaNacimiento, fechaLlegada, habitat, observaciones, sexo, imagen
        FROM animal
        WHERE idAnimal = %s
    """,(idAnimal,)) 
    animal = cur.fetchone()

    cur.close()
    conn.close()

    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    img_url = url_for('static', filename='uploads/'+ animal["imagen"], _external=True)
    html = render_template("pdfAnimal.html", animal=animal, img_url=img_url)

    options = {'enable-local-file-access':None}

    pdf=pdfkit.from_string(html, False, configuration=config, options=options)


    response = make_response(pdf)
    response.headers["content-Type"]="application/pdf"
    response.headers["content-Disposition"] = "inline; filename=animal.pdf"
    return response


@animales.route("/eliminar_animal/<int:idAnimal>", methods=["POST"])
def eliminar_animal(idAnimal):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM animal WHERE idAnimal=%s",(idAnimal,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("animales.ver_animales"))
