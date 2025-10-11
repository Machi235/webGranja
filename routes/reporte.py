from flask import Flask, render_template, request, Blueprint
from db import get_connection

reporte = Blueprint('reporte', __name__)

# Ruta para mostrar todos los reportes
@reporte.route('/reportes', methods=['GET', 'POST'])
def reportes():
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    query = "SELECT * FROM vista_reportes WHERE 1=1"
    params = []

    # Filtros (opcional)
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        if tipo:
            query += " AND tipo = %s"
            params.append(tipo)

    query += " ORDER BY fecha DESC"

    cursor.execute(query, params)
    reportes = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('reporte.html', reportes=reportes)


# Ruta para mostrar detalle de un reporte específico
@reporte.route('/reportes/<int:id_registro>')
def detalle_reporte(id_registro):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vista_reportes WHERE id_registro = %s", (id_registro,))
    reporte = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not reporte:
        return "Reporte no encontrado", 404

    return render_template('detalle_reporte.html', reporte=reporte)
