from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

reporte = Blueprint('reporte', __name__)

# ==========================================================
# 🔹 Mostrar todos los reportes de un animal (con filtro)
# ==========================================================
@reporte.route('/reportes/<int:id_animal>', methods=['GET', 'POST'])
def reportes(id_animal):
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        query = "SELECT * FROM vista_reportes WHERE idAnimal = %s"
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


# ==========================================================
# 🔹 Mostrar detalle de un reporte
# ==========================================================
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


# ==========================================================
# 🔹 Eliminar (desactivar) un reporte
# ==========================================================
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


# ==========================================================
# 🔹 Editar un reporte
# ==========================================================
@reporte.route("/reportes/editar/<int:id_registro>", methods=["GET", "POST"])
def editar_reporte(id_registro):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Primero averiguar el tipo de reporte
    cur.execute("SELECT tipo, idAnimal FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    info = cur.fetchone()
    if not info:
        flash(" Reporte no encontrado en la vista", "danger")
        return redirect(url_for("reporte.reportes", id_animal=1))

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
        return redirect(url_for("reporte.reportes", id_animal=id_animal))

    tabla, campo_id = tablas[tipo]

    # Obtener todos los datos del registro actual
    cur.execute(f"SELECT * FROM {tabla} WHERE {campo_id} = %s", (id_registro,))
    reporte = cur.fetchone()

    if not reporte:
        flash(" No se encontró el reporte original", "danger")
        return redirect(url_for("reporte.reportes", id_animal=id_animal))

    if request.method == "POST":
        # Actualizar dinámicamente los campos que llegan
        datos_actualizados = request.form.to_dict()
        campos = ", ".join([f"{k} = %s" for k in datos_actualizados.keys()])
        valores = list(datos_actualizados.values())
        valores.append(id_registro)

        query = f"UPDATE {tabla} SET {campos} WHERE {campo_id} = %s"
        cur.execute(query, valores)
        conn.commit()

        flash(" Reporte actualizado correctamente", "success")
        return redirect(url_for("reporte.detalle_reporte", id_registro=id_registro))

    cur.close()
    conn.close()
    return render_template("editar_reporte.html", reporte=reporte, tipo=tipo)
