from flask import Blueprint, render_template, request, redirect, url_for
from db import get_connection

bp = Blueprint('buscarHabitat', __name__, url_prefix="/habitat")

@bp.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultados = []
    busqueda = None

    if request.method == 'POST':
        busqueda = request.form['nombre_habitat']
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        query = """
            SELECT h.idHabitat, h.nombreHabitat, h.estado, h.tipo, h.ubicacion,
                   a.nombre AS nombreAnimal, a.estadoSalud, a.sexo, a.imagen
            FROM habitat h
            LEFT JOIN animal a ON a.habitat = h.idHabitat
            WHERE h.nombreHabitat LIKE %s
        """
        cursor.execute(query, ("%" + busqueda + "%",))
        resultados = cursor.fetchall()

        cursor.close()
        conexion.close()

    return render_template('buscarHabitat.html', resultados=resultados, busqueda=busqueda)



