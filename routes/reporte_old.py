from flask import Flask, render_template, request, Blueprint
from db import get_connection

reporte = Blueprint('reporte', __name__)

# 🔹 Ruta para mostrar los reportes de un animal específico
@reporte.route('/reportes/<int:id_animal>', methods=['GET', 'POST'])
def reportes(id_animal):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    query = "SELECT * FROM vista_reportes WHERE idAnimal = %s"
    params = [id_animal]

    # Filtros opcionales
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        fecha = request.form.get('fecha')

        if tipo:
            query += " AND tipo = %s"
            params.append(tipo)
        if fecha:
            query += " AND fecha = %s"
            params.append(fecha)

    query += " ORDER BY fecha DESC"

    cursor.execute(query, params)
    reportes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('reporte.html', reportes=reportes, id_animal=id_animal)

# 🔹 Ruta para mostrar el detalle de un reporte
@reporte.route('/reportes/detalle/<int:id_registro>')
def detalle_reporte(id_registro):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    reporte = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not reporte:
        return "Reporte no encontrado", 404

    return render_template('reporte.html', reporte=reporte)

