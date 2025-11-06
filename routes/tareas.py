from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection

tareas = Blueprint('tareas', __name__)

@tareas.route('/tareas')
def listar_tareas():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.idTarea, t.nombreTarea, t.descripcion, t.prioridad, 
               t.fechaInicio, t.fechaFin, t.estado,
               u.nombre AS empleado, u.rol
        FROM tareas t
        JOIN usuarios u ON t.idUsuario = u.idUsuario
        ORDER BY t.idTarea DESC
    """)
    tareas = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('tareas_lista.html', tareas=tareas)


#  Crear nueva tarea
@tareas.route('/tareas/nueva', methods=['GET', 'POST'])
def nueva_tarea():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Obtener lista de empleados (no admins)
    cur.execute("SELECT idUsuario, nombre, rol FROM usuarios WHERE rol != 'Admin'")
    empleados = cur.fetchall()

    if request.method == 'POST':
        nombreTarea = request.form['nombreTarea']
        descripcion = request.form['descripcion']
        prioridad = request.form['prioridad']
        fechaInicio = request.form['fechaInicio']
        fechaFin = request.form['fechaFin']
        idUsuario = request.form['idUsuario']

        cur.execute("""
            INSERT INTO tareas (nombreTarea, descripcion, prioridad, fechaInicio, fechaFin, idUsuario)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombreTarea, descripcion, prioridad, fechaInicio, fechaFin, idUsuario))
        conn.commit()

        flash("✅ Tarea creada correctamente", "success")
        return redirect(url_for('tareas.listar_tareas'))

    cur.close()
    conn.close()
    return render_template('tareas_form.html', empleados=empleados, tarea=None)


#  Editar tarea
@tareas.route('/tareas/editar/<int:id>', methods=['GET', 'POST'])
def editar_tarea(id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM tareas WHERE idTarea = %s", (id,))
    tarea = cur.fetchone()

    cur.execute("SELECT idUsuario, nombre, rol FROM usuarios WHERE rol != 'Admin'")
    empleados = cur.fetchall()

    if request.method == 'POST':
        nombreTarea = request.form['nombreTarea']
        descripcion = request.form['descripcion']
        prioridad = request.form['prioridad']
        fechaInicio = request.form['fechaInicio']
        fechaFin = request.form['fechaFin']
        idUsuario = request.form['idUsuario']
        estado = request.form['estado']

        cur.execute("""
            UPDATE tareas
            SET nombreTarea=%s, descripcion=%s, prioridad=%s, 
                fechaInicio=%s, fechaFin=%s, idUsuario=%s, estado=%s
            WHERE idTarea=%s
        """, (nombreTarea, descripcion, prioridad, fechaInicio, fechaFin, idUsuario, estado, id))
        conn.commit()

        flash("✅ Tarea actualizada correctamente", "success")
        return redirect(url_for('tareas.listar_tareas'))

    cur.close()
    conn.close()
    return render_template('tareas_form.html', tarea=tarea, empleados=empleados)


# Eliminar tarea
@tareas.route('/tareas/eliminar/<int:id>')
def eliminar_tarea(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tareas WHERE idTarea = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Tarea eliminada correctamente", "info")
    return redirect(url_for('tareas.listar_tareas'))


#  Listar solo tareas pendientes
@tareas.route('/tareas/pendientes')
def tareas_pendientes():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.idTarea, t.nombreTarea, t.descripcion, t.prioridad, 
               t.fechaInicio, t.fechaFin, t.estado,
               u.nombre AS empleado
        FROM tareas t
        JOIN usuarios u ON t.idUsuario = u.idUsuario
        WHERE t.estado = 'Pendiente'
        ORDER BY t.prioridad DESC
    """)
    pendientes = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('tareas_pendientes.html', pendientes=pendientes)


# Cambiar estado de tarea (realizada / no realizada)
@tareas.route('/tareas/cambiar_estado/<int:id>/<string:estado>')
def cambiar_estado(id, estado):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tareas SET estado = %s WHERE idTarea = %s", (estado, id))
    conn.commit()
    cur.close()
    conn.close()
    flash("🔄 Estado de tarea actualizado", "success")
    return redirect(url_for('tareas.tareas_pendientes'))
