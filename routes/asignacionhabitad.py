from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection
import datetime

asignacion = Blueprint('asignacion', __name__)

@asignacion.route('/asignar', methods=['GET', 'POST'])
def asignar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Traer animales y hábitats para mostrar en el formulario
    cursor.execute("SELECT * FROM animal")
    animales = cursor.fetchall()

    cursor.execute("SELECT * FROM habitat")
    habitats = cursor.fetchall()

    if request.method == 'POST':
        animal_id = request.form['animal_id']
        habitat_id = request.form['habitat_id']

        # Validar capacidad
        cursor.execute("SELECT COUNT(*) as ocupados FROM asignacion WHERE habitat_id=%s", (habitat_id,))
        ocupados = cursor.fetchone()['ocupados']

        cursor.execute("SELECT capacidad_max, especie_compatible FROM habitat WHERE id=%s", (habitat_id,))
        habitat = cursor.fetchone()

        cursor.execute("SELECT especie FROM animal WHERE id=%s", (animal_id,))
        animal = cursor.fetchone()

        if ocupados >= habitat['capacidad_max']:
            flash("El hábitat ya está en su capacidad máxima.", "error")
        elif animal['especie'] != habitat['especie_compatible']:
            flash("El hábitat no es compatible con la especie del animal.", "error")
        else:
            cursor.execute("""
                INSERT INTO asignacion (animal_id, habitat_id, fecha_asignacion)
                VALUES (%s, %s, %s)
            """, (animal_id, habitat_id, datetime.date.today()))
            conn.commit()
            flash("Animal asignado correctamente.", "success")
            return redirect(url_for('asignacion.asignar'))

    cursor.close()
    conn.close()
    return render_template('asignacionhabitad.html', animales=animales, habitats=habitats)
