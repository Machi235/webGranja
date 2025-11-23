import os
from flask import Blueprint, make_response, render_template, request, redirect, url_for, flash
from db import get_connection
from io import BytesIO #Modulo de entradas y salidas
from reportlab.lib.pagesizes import letter #tamaño de papel
from reportlab.lib.styles import getSampleStyleSheet #Estilos de texto
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image #Contenido de pdf
from reportlab.lib.units import cm #Usar unidades de medida 

reporte = Blueprint('reporte', __name__)


@reporte.route('/reportes/<int:id_animal>', methods=['GET', 'POST'])
def reportes(id_animal):
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        
        query = "SELECT * FROM vista_reportes WHERE idAnimal = %s AND activo = 1"
        params = [id_animal]

        if request.method == "POST":
            tipo = request.form.get("tipo")
            fecha = request.form.get("fecha")

            if tipo:
               query += " AND CONVERT(tipo USING utf8mb4) COLLATE utf8mb4_unicode_ci = CONVERT(%s USING utf8mb4) COLLATE utf8mb4_unicode_ci"
               params.append(tipo)

            if fecha:
                query += " AND fecha = %s"
                params.append(fecha)

        query += " ORDER BY fecha DESC"
        cur.execute(query, params)
        reportes = cur.fetchall()

        cur.close()
        conn.close()

        return render_template("registros_medicos.html", registros=reportes, id_animal=id_animal)

    except Exception as e:
        print("❌ Error en /reportes:", str(e))
        flash(f"Ocurrió un error al cargar los reportes: {str(e)}", "danger")
        return redirect(url_for("animales.ver_animal", idAnimal=id_animal))




@reporte.route('/reportes/detalle/<int:id_registro>')
def detalle_reporte(id_registro):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Obtener tipo de evento y id del animal
    cur.execute("SELECT tipo, idAnimal FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    info = cur.fetchone()

    if not info:
        flash("❌ Reporte no encontrado", "danger")
        return redirect(url_for('reporte.reportes', id_animal=1))

    tipo = info['tipo'].strip().lower()
    id_animal = info['idAnimal']

    tablas = {
        'vacuna': ('vacuna', 'idVacuna'),
        'postoperatorio': ('postoperatorio', 'idPostoperatorio'),
        'terapia física': ('terapiafisica', 'idTerapia'),
        'terapiafisica': ('terapiafisica', 'idTerapia'),
        'visita': ('visitas', 'idVisitas'),
        'visitas': ('visitas', 'idVisitas'),
        'medicación': ('medicacion', 'idMed'),
        'medicacion': ('medicacion', 'idMed'),
        'cirugia': ('cirugia', 'idCirugia'),
        'cirugía': ('cirugia', 'idCirugia')
    }

    if tipo not in tablas:
        flash(f"Tipo '{tipo}' no reconocido", "danger")
        return redirect(url_for('reporte.reportes', id_animal=id_animal))

    tabla, campo_id = tablas[tipo]

    # Obtener todos los campos del reporte
    cur.execute(f"SELECT * FROM {tabla} WHERE {campo_id} = %s", (id_registro,))
    reporte = cur.fetchone()

    cur.close()
    conn.close()

    if not reporte:
        flash(" No se encontró el detalle del reporte", "warning")
        return redirect(url_for('reporte.reportes', id_animal=id_animal))

    # PASAMOS id_registro AL TEMPLATE
    return render_template("detalle_reporte.html", reporte=reporte, tipo=tipo, id_registro=id_registro, id_animal=id_animal)



@reporte.route('/reportes/eliminar', methods=['POST'])
def eliminar_reporte():
    try:
        id_registro = request.form.get('id_registro')
        tipo = request.form.get('tipo', '').strip().lower()
        id_animal = request.form.get('id_animal')

        print("========== DATOS RECIBIDOS ==========")
        print(f"id_registro: {id_registro}")
        print(f"tipo: {tipo}")
        print(f"id_animal: {id_animal}")
        print("=====================================")

        if not id_registro or not tipo or not id_animal:
            flash("Faltan datos para eliminar el registro", "danger")
            return redirect(request.referrer or url_for('reporte.reportes', id_animal=1))

        conn = get_connection()
        cur = conn.cursor()

        tablas = {
            'vacuna': ('vacuna', 'idVacuna'),
            'postoperatorio': ('postoperatorio', 'idPostoperatorio'),
            'terapia física': ('terapiafisica', 'idTerapia'),
            'terapiafisica': ('terapiafisica', 'idTerapia'),
            'visita': ('visitas', 'idVisitas'),
            'medicación': ('medicacion', 'idMed'),
            'medicacion': ('medicacion', 'idMed'),
            'cirugia': ('cirugia', 'idCirugia'),
            'cirugía': ('cirugia', 'idCirugia')
        }

        tipo_normalizado = tipo.lower().strip()
        if tipo_normalizado not in tablas:
            flash(f" Tipo de evento '{tipo}' no reconocido", "danger")
            return redirect(url_for('reporte.reportes', id_animal=id_animal))

        tabla, campo_id = tablas[tipo_normalizado]

        query = f"UPDATE {tabla} SET activo = 0 WHERE {campo_id} = %s"
        cur.execute(query, (id_registro,))

        if cur.rowcount > 0:
            conn.commit()
            flash(f"{tipo.capitalize()} eliminado correctamente", "success")
        else:
            conn.rollback()
            flash("No se encontró el registro a eliminar", "warning")

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        print(f" Error al eliminar: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f" Error al eliminar: {str(e)}", "danger")

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

    return redirect(url_for('reporte.reportes', id_animal=id_animal))


@reporte.route("/reportes/editar/<int:id_registro>", methods=["GET", "POST"])
def editar_reporte(id_registro):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    try:
        
        cur.execute("SELECT tipo, idAnimal FROM vista_reportes WHERE id_registro = %s", (id_registro,))
        info = cur.fetchone()

        if not info:
            flash("❌ No se encontró el reporte en la vista", "danger")
            return redirect(url_for("reporte.reportes", id_animal=1))

        tipo = info["tipo"].strip().lower()
        id_animal = info["idAnimal"]

        tablas = {
            'vacuna': ('vacuna', 'idVacuna'),
            'postoperatorio': ('postoperatorio', 'idPostoperatorio'),
            'terapia física': ('terapiafisica', 'idTerapia'),
            'terapiafisica': ('terapiafisica', 'idTerapia'),
            'visita': ('visitas', 'idVisitas'),
            'visitas': ('visitas', 'idVisitas'),
            'medicación': ('medicacion', 'idMed'),
            'medicacion': ('medicacion', 'idMed'),
            'cirugia': ('cirugia', 'idCirugia'),
            'cirugía': ('cirugia', 'idCirugia')
        }

        if tipo not in tablas:
            flash(f"Tipo '{tipo}' no reconocido", "danger")
            return redirect(url_for("reporte.reportes", id_animal=id_animal))

        tabla, campo_id = tablas[tipo]

        cur.execute(f"SELECT * FROM {tabla} WHERE {campo_id} = %s", (id_registro,))
        reporte = cur.fetchone()

        if not reporte:
            flash("❌ No se encontró el registro en su tabla real", "warning")
            return redirect(url_for("reporte.reportes", id_animal=id_animal))

        if request.method == "POST":

            datos = request.form.to_dict()

            if not datos:
                flash("No se enviaron datos", "warning")
                return redirect(url_for("reporte.editar_reporte", id_registro=id_registro))

            campos = ", ".join([f"{k} = %s" for k in datos.keys()])
            valores = list(datos.values())
            valores.append(id_registro)

            query = f"UPDATE {tabla} SET {campos} WHERE {campo_id} = %s"
            cur.execute(query, valores)
            conn.commit()

            flash("✔️ Reporte actualizado correctamente", "success")
            return redirect(url_for("reporte.detalle_reporte", id_registro=id_registro))

        return render_template(
            "editar_reporte.html",
            reporte=reporte,
            tipo=tipo,
            id_registro=id_registro,
            id_animal=id_animal
        )

    finally:
        cur.close()
        conn.close()

@reporte.route("/reportes/pdf/<int:id_registro>")
def pdf_reporte(id_registro):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # 1. Averiguar tipo y animal desde la vista
    cur.execute("SELECT tipo, idAnimal FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    info = cur.fetchone()

    if not info:
        flash("No se encontró el reporte", "danger")
        return redirect(url_for("reporte.reportes", id_animal=1))

    tipo = info["tipo"].strip().lower()
    id_animal = info["idAnimal"]

    # Tabla + campo PK según el tipo
    tablas = {
        'vacuna': ('vacuna', 'idVacuna'),
        'postoperatorio': ('postoperatorio', 'idPostoperatorio'),
        'terapia física': ('terapiafisica', 'idTerapia'),
        'terapiafisica': ('terapiafisica', 'idTerapia'),
        'visita': ('visitas', 'idVisitas'),
        'visitas': ('visitas', 'idVisitas'),
        'medicación': ('medicacion', 'idMed'),
        'medicacion': ('medicacion', 'idMed'),
        'cirugia': ('cirugia', 'idCirugia'),
        'cirugía': ('cirugia', 'idCirugia')
    }

    if tipo not in tablas:
        flash("Tipo no reconocido", "danger")
        return redirect(url_for("reporte.reportes", id_animal=id_animal))

    tabla, campo_id = tablas[tipo]

    # 2. Obtener todos los campos del reporte real
    cur.execute(f"SELECT * FROM {tabla} WHERE {campo_id} = %s", (id_registro,))
    reporte = cur.fetchone()

    # 3. Cargar datos del animal
    cur.execute("SELECT nombre, especie, imagen FROM animal WHERE idAnimal = %s", (id_animal,))
    animal = cur.fetchone()

    cur.close()
    conn.close()

    # ==========================
    # 4. CREACIÓN DEL PDF
    # ==========================
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título dinámico
    titulo = f"Reporte de {tipo.capitalize()}"
    elements.append(Paragraph(f"<b>{titulo}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Imagen del animal
    if animal.get("imagen"):
        ruta_imagen = os.path.join("static/uploads", animal["imagen"])
        img = Image(ruta_imagen, width=5*cm, height=5*cm)
        img.hAlign = "CENTER"
        elements.append(img)
        elements.append(Spacer(1, 12))

    # ==========================
    # 5. CONTENIDO DINÁMICO
    # ==========================

    # Datos básicos del animal
    contenido = f"""
    <b>Animal:</b> {animal['nombre']}<br/>
    <b>Especie:</b> {animal['especie']}<br/><br/>
    """

    # Agregar todos los campos del reporte dinámicamente
    for campo, valor in reporte.items():
        if campo in [campo_id, "idAnimal", "activo"]:
            continue  # Campos que no queremos mostrar

        contenido += f"<b>{campo}:</b> {valor}<br/><br/>"

    elements.append(Paragraph(contenido, styles["Normal"]))
    elements.append(Spacer(1, 20))

    pdf.build(elements)

    # Respuesta final
    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"inline; filename={tipo}.pdf"

    return response