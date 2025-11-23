from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

reporte = Blueprint('reporte', __name__)


# ================================
#  LISTADO DE REPORTES
# ================================
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
                query += " AND tipo = %s"
                params.append(tipo)

            if fecha:
                query += " AND DATE(fecha) = %s"
                params.append(fecha)

        query += " ORDER BY fecha DESC"
        cur.execute(query, params)
        reportes = cur.fetchall()

        cur.close()
        conn.close()

        return render_template("registros_medicos.html", registros=reportes, id_animal=id_animal)

    except Exception as e:
        flash(f"Error cargando reportes: {str(e)}", "danger")
        return redirect(url_for("animales.ver_animal", idAnimal=id_animal))



# ================================
#  DETALLE DE REPORTE
# ================================
@reporte.route('/reportes/detalle/<int:id_registro>')
def detalle_reporte(id_registro):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT tipo, idAnimal FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    info = cur.fetchone()

    if not info:
        flash("Reporte no encontrado", "danger")
        return redirect(url_for('reporte.reportes', id_animal=1))

    tipo = info['tipo'].strip().lower()
    id_animal = info['idAnimal']

    tablas = {
        'vacuna': ('vacuna', 'idVacuna'),
        'postoperatorio': ('postoperatorio', 'idPostoperatorio'),
        'terapiafisica': ('terapiafisica', 'idTerapia'),
        'visita': ('visitas', 'idVisitas'),
        'medicacion': ('medicacion', 'idMed'),
        'cirugia': ('cirugia', 'idCirugia')
    }

    if tipo not in tablas:
        flash("Tipo no reconocido", "danger")
        return redirect(url_for('reporte.reportes', id_animal=id_animal))

    tabla, campo_id = tablas[tipo]

    cur.execute(f"SELECT * FROM {tabla} WHERE {campo_id} = %s", (id_registro,))
    reporte = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "detalle_reporte.html",
        reporte=reporte,
        tipo=tipo,
        id_registro=id_registro,
        id_animal=id_animal
    )



# ================================
#  ELIMINAR REPORTE
# ================================
@reporte.route('/reportes/eliminar', methods=['POST'])
def eliminar_reporte():
    id_registro = request.form.get('id_registro')
    tipo = request.form.get('tipo', '').strip().lower()
    id_animal = request.form.get('id_animal')

    tablas = {
        'vacuna': ('vacuna', 'idVacuna'),
        'postoperatorio': ('postoperatorio', 'idPostoperatorio'),
        'terapiafisica': ('terapiafisica', 'idTerapia'),
        'visita': ('visitas', 'idVisitas'),
        'medicacion': ('medicacion', 'idMed'),
        'cirugia': ('cirugia', 'idCirugia')
    }

    if tipo not in tablas:
        flash("Tipo no reconocido", "danger")
        return redirect(url_for("reporte.reportes", id_animal=id_animal))

    tabla, campo_id = tablas[tipo]

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(f"UPDATE {tabla} SET activo = 0 WHERE {campo_id} = %s", (id_registro,))
        conn.commit()
        flash("Registro eliminado correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error eliminando: {str(e)}", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('reporte.reportes', id_animal=id_animal))



# ================================
#  EDITAR REPORTE
# ================================
@reporte.route("/reportes/editar/<int:id_registro>", methods=["GET", "POST"])
def editar_reporte(id_registro):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT tipo, idAnimal FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    info = cur.fetchone()

    if not info:
        flash("Reporte no encontrado", "danger")
        return redirect(url_for("reporte.reportes", id_animal=1))

    tipo = info["tipo"].strip().lower()
    id_animal = info["idAnimal"]

    tablas = {
        'vacuna': ('vacuna', 'idVacuna'),
        'postoperatorio': ('postoperatorio', 'idPostoperatorio'),
        'terapiafisica': ('terapiafisica', 'idTerapia'),
        'visita': ('visitas', 'idVisitas'),
        'medicacion': ('medicacion', 'idMed'),
        'cirugia': ('cirugia', 'idCirugia')
    }

    if tipo not in tablas:
        flash("Tipo no reconocido", "danger")
        return redirect(url_for("reporte.reportes", id_animal=id_animal))

    tabla, campo_id = tablas[tipo]

    cur.execute(f"SELECT * FROM {tabla} WHERE {campo_id} = %s", (id_registro,))
    reporte = cur.fetchone()

    if request.method == "POST":
        datos = request.form.to_dict()
        campos = ", ".join([f"{k} = %s" for k in datos.keys()])
        valores = list(datos.values()) + [id_registro]
        cur.execute(f"UPDATE {tabla} SET {campos} WHERE {campo_id} = %s", valores)
        conn.commit()
        flash("Reporte actualizado correctamente", "success")
        return redirect(url_for("reporte.detalle_reporte", id_registro=id_registro))

    cur.close()
    conn.close()

    return render_template(
        "editar_reporte.html",
        reporte=reporte,
        tipo=tipo,
        id_registro=id_registro,
        id_animal=id_animal
    )
