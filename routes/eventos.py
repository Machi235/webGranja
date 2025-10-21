from flask import render_template, Blueprint
from db import get_connection

eventos_general = Blueprint('eventos_general', __name__)

@eventos_general.route('/animales/<int:id_animal>/eventos')
def ver_eventos(id_animal):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vista_reportes WHERE id_animal = %s ORDER BY fecha DESC", (id_animal,))
    eventos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template('eventos_animal.html', eventos=eventos, id_animal=id_animal)
