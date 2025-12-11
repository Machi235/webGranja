import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, flash
from werkzeug.utils import secure_filename
from io import BytesIO #Modulo de entradas y salidas
from reportlab.lib.pagesizes import letter #tamaño de papel
from reportlab.lib.styles import getSampleStyleSheet #Estilos de texto
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image #Contenido de pdf
from reportlab.lib.units import cm #Usar unidades de medida 
from db import get_connection
from flask import session



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
            # Datos del formulario
            nombre = request.form.get("nombre")
            especie = request.form.get("especie")
            salud = request.form.get("salud")
            edad = request.form.get("edad")
            nacimiento = request.form.get("fechaNacimiento")
            llegada = request.form.get("fechaLlegada")
            habitat = request.form.get("habitat")
            observaciones = request.form.get("observaciones")
            sexo = request.form.get("sexo")

            # Validación de campos obligatorios
            if not nombre or not especie or not salud or not edad or not habitat or not sexo:
                return jsonify({"error": "Faltan campos obligatorios"}), 400

            # Validar especie
            cur.execute("SELECT COUNT(*) AS total FROM especie WHERE idEspecie = %s", (especie,))
            result = cur.fetchone()
            if result["total"] == 0:
                return jsonify({"error": "La especie seleccionada no existe"}), 400

            # Validar hábitat
            cur.execute("SELECT COUNT(*) AS total FROM habitat WHERE idHabitat = %s", (habitat,))
            result = cur.fetchone()
            if result["total"] == 0:
                return jsonify({"error": "El hábitat seleccionado no existe"}), 400

            # Guardar imagen
            archivo = request.files.get("imagen")
            filename = None
            if archivo and archivo.filename != "":
                filename = secure_filename(archivo.filename)
                archivo.save(os.path.join(UPLOAD_FOLDER, filename))

            # Guardar el animal
            cur.callproc("limite_de_habitat",(nombre, especie, salud, edad, nacimiento, llegada, habitat, observaciones, sexo, filename))
            for result in cur.stored_results():
                animal= result.fetchall()
                if animal:
                    mensaje = animal[0]['mensaje']
                    print("Mensaje del procedimiento:", mensaje)
            conn.commit()
            if "asignado" in mensaje.lower():
                return jsonify({"status": "success", "message": mensaje})
            else:
                return jsonify({"status": "warning", "message": mensaje})
        except Exception as e:
            print("Error al registrar animal:", str(e))
            return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500
        
    cur.execute("SELECT idEspecie, tipoEspecie FROM especie ORDER BY tipoEspecie")
    especies = cur.fetchall()

    cur.execute("""select count(idAnimal) as animales, idHabitat, nombreHabitat, capacidad from habitat as h left join animal as a on a.habitat=h.idHabitat and 
                a.activo = 1 where h.activo=1 group by h.idHabitat having animales < capacidad""")
    habitats = cur.fetchall()

# Notificaciones RRHH para navRrhh.html
    notificaciones_no_leidas = 0
    notificaciones = []
    if 'idUsuario' in session:
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session['idUsuario'],))
        notificaciones = cur.fetchall()
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))

    cur.close()
    conn.close()
    return render_template(
        "crearAnimal.html",
        especies=especies,
        habitats=habitats,
        rol=session.get("rol"),
        notificaciones_no_leidas=notificaciones_no_leidas,
        notificaciones=notificaciones
)



@animales.route("/ver_animales", methods=["GET"])
def ver_animales():
    """Muestra todos los animales registrados"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Obtener todos los animales
    cur.execute("""
        SELECT idAnimal, nombre, tipoEspecie, estadoSalud, edad, fechaNacimiento, fechaLlegada, nombreHabitat, observaciones, sexo, imagen FROM animal as a 
        INNER JOIN habitat as h on habitat = h.idHabitat INNER JOIN especie as e on a.especie = e.idEspecie
        ORDER BY nombre
    """)
    animales = cur.fetchall()

    # Filtros
    cur.execute("SELECT idEspecie, tipoEspecie FROM especie")
    especies = cur.fetchall()

    cur.execute("SELECT DISTINCT estadoSalud FROM animal")
    estados = [row["estadoSalud"] for row in cur.fetchall()]

    # Notificaciones y rol
    notificaciones_no_leidas = 0
    notificaciones = []
    if 'idUsuario' in session:
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session['idUsuario'],))
        notificaciones = cur.fetchall()
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))

    cur.close()
    conn.close()

    return render_template(
        "verAnimal.html",
        animales=animales,
        especies=especies,
        estados=estados,
        rol=session.get("rol"),
        notificaciones_no_leidas=notificaciones_no_leidas,
        notificaciones=notificaciones
    )


@animales.route("/detalle_animal/<int:idAnimal>")
def ver_animal(idAnimal):
    """Muestra la información completa de un solo animal"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(""" SELECT idAnimal, nombre, tipoEspecie, estadoSalud, edad, fechaNacimiento, fechaLlegada, nombreHabitat, observaciones, sexo, imagen FROM animal as a 
                INNER JOIN habitat as h on habitat = h.idHabitat INNER JOIN especie as e on a.especie = e.idEspecie WHERE idAnimal = %s """, (idAnimal,))
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
        SELECT idAnimal, nombre, tipoEspecie, estadoSalud, edad, fechaNacimiento, fechaLlegada, nombreHabitat, observaciones, sexo, imagen FROM animal as a 
                INNER JOIN habitat as h on habitat = h.idHabitat INNER JOIN especie as e on a.especie = e.idEspecie WHERE idAnimal = %s """, (idAnimal,))
    animal = cur.fetchone()

    buffer = BytesIO() #Crea un espacio temporal en memoria
    pdf = SimpleDocTemplate(buffer, pagesize=letter) #Se crea el documento pdf
    elements = [] #Lista vacia donde se pone el contenido
    styles = getSampleStyleSheet() #conjunto de estilos 

    elements.append(Paragraph(f"<b>Ficha del animal</b>", styles["Title"])) #Agrgar un parrafro al pdf

    ruta_imagen = os.path.join("static/uploads", animal["imagen"]) #Une la ruta base con el nombre de la imagen
    img = Image(ruta_imagen, width=8*cm, height=8*cm) #Carga la imagen ajustandolo al tamaño
    img.hAlign = "CENTER" #Ajusta la imagen
    elements.append(img)
    elements.append(Spacer(1, 30))

    contenido = f"""
    <b>Nombre:</b>{animal['nombre']}<br/>
    <b>Especie:</b>{animal['tipoEspecie']}<br/>
    <b>Estado salud:</b>{animal['estadoSalud']}<br/>
    <b>Edad:</b>{animal['edad']}<br/>
    <b>Fecha de nacimiento:</b>{animal['fechaNacimiento']}<br/>
    <b>Fecha de llegada:</b>{animal['fechaLlegada']}<br/>
    <b>Habitat:</b>{animal['nombreHabitat']}<br/>
    <b>Observaciones:</b>{animal['observaciones']}<br/>
    <b>Sexo:</b>{animal['sexo']}<br/>"""

    styles = getSampleStyleSheet()
    estilo_grande = styles["Normal"].clone('estilo_grande')
    estilo_grande.fontSize = 14   # tamaño de letra
    estilo_grande.leading = 37    # espacio entre líneas

    elements.append(Paragraph(contenido, estilo_grande))


    pdf.build(elements) #Crea el pdf con todos elementos en el mismo orden  

    response = make_response(buffer.getvalue()) # sE crea una respuesta http con los bytes obtenidos en el buffer    
    response.headers["Content-Type"] = "application/pdf" #Dice que el contenido es un pdf
    response.headers["Content-Disposition"] = "inline; filename=animal.pdf" #Lo abre directamente
    return response 


@animales.route("/eliminar_animal/<int:idAnimal>", methods=["POST"])
def eliminar_animal(idAnimal):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM animal WHERE idAnimal=%s", (idAnimal,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("animales.ver_animales"))

@animales.route("/registros_medicos/<int:id_animal>", methods=["GET", "POST"])
def registros_medicos(id_animal):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # --- Filtros ---
    tipo = request.form.get("tipo") if request.method == "POST" else request.args.get("tipo")
    fecha = request.form.get("fecha") if request.method == "POST" else request.args.get("fecha")

    # --- Paginación ---
    pagina = int(request.args.get("page", 1))
    por_pagina = 6
    offset = (pagina - 1) * por_pagina

    # --- Contar total de registros filtrados ---
    count_query = "SELECT COUNT(*) AS total FROM vista_reportes WHERE idAnimal = %s"
    params = [id_animal]

    if tipo:
        count_query += " AND tipo = %s"
        params.append(tipo)
    if fecha:
        count_query += " AND fecha = %s"
        params.append(fecha)

    cur.execute(count_query, params)
    total_registros = cur.fetchone()["total"]
    total_paginas = (total_registros + por_pagina - 1) // por_pagina

    # --- Obtener registros paginados ---
    query = """
        SELECT id_registro, tipo, descripcion, fecha 
        FROM vista_reportes 
        WHERE idAnimal = %s
    """
    params = [id_animal]

    if tipo:
        query += " AND tipo = %s"
        params.append(tipo)
    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)

    query += " ORDER BY fecha ASC LIMIT %s OFFSET %s"
    params.extend([por_pagina, offset])

    cur.execute(query, params)
    registros = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "registros_medicos.html",
        registros=registros,
        id_animal=id_animal,
        pagina=pagina,
        total_paginas=total_paginas,
        has_prev=pagina > 1,
        has_next=pagina < total_paginas,
        tipo=tipo,
        fecha=fecha
    )

@animales.route("/detalle_registro/<int:id_registro>")
def detalle_registro(id_registro):
    """Muestra el detalle completo de un registro (formulario)"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    registro = cur.fetchone()

    cur.close()
    conn.close()

    if not registro:
        return "Registro no encontrado", 404

    # 🔹 Aquí cambiamos el template (antes estaba mal)
    return render_template("detalle_reporte.html", reporte=registro)

@animales.route("/Reasignar-animal/<int:idAnimal>", methods=["GET"])
def editar_animal(idAnimal):
    conn=get_connection()
    cur=conn.cursor(dictionary=True)

    cur.execute("select count(*) as animales, idHabitat, habitat, nombreHabitat, capacidad from animal as a inner join habitat as h on a.habitat=h.idHabitat where h.activo = 1 group by habitat having animales < capacidad")
    habitats = cur.fetchall()

    cur.execute("""
        SELECT idAnimal, habitat, nombre, tipoEspecie, estadoSalud, edad, fechaNacimiento, fechaLlegada, nombreHabitat, observaciones, sexo, imagen FROM animal as a 
        INNER JOIN habitat as h on habitat = h.idHabitat INNER JOIN especie as e on a.especie = e.idEspecie WHERE idAnimal = %s """, (idAnimal,))
    animal = cur.fetchone()
    
    conn.close()
    cur.close()

    return render_template("editarAnimal.html", animal=animal , habitats=habitats)

@animales.route("/Actualizar-animal/<int:idAnimal>", methods=["POST"])
def actualizar_animal(idAnimal):

    habitat = request.form.get("habitat")
 
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" UPDATE animal SET habitat = %s WHERE idAnimal = %s """, 
                (habitat, idAnimal))
    
    conn.commit()

    cur.close()
    conn.close()

    return redirect (url_for("animales.ver_animales"))
