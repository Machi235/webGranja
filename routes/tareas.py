from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection 
tareas = Blueprint('tareas', __name__)

# =====================================================
# LISTAR TAREAS
# =====================================================
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
    tareas_list = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('tareas_lista.html', tareas=tareas_list)


# =====================================================
# CREAR NUEVA TAREA
# =====================================================
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


# =====================================================
# EDITAR TAREA — BLOQUEADA SI ESTÁ REALIZADA
# =====================================================
@tareas.route('/tareas/editar/<int:id>', methods=['GET', 'POST'])
def editar_tarea(id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Buscar tarea
    cur.execute("SELECT * FROM tareas WHERE idTarea = %s", (id,))
    tarea = cur.fetchone()

    if not tarea:
        flash("❌ La tarea no existe", "danger")
        return redirect(url_for('tareas.listar_tareas'))

    # ❌ Bloquear edición si está realizada
    if tarea['estado'] == 'Realizada':
        flash("⚠️ Esta tarea ya está marcada como realizada y no puede editarse", "warning")
        return redirect(url_for('tareas.listar_tareas'))

    # Obtener lista de empleados
    cur.execute("SELECT idUsuario, nombre, rol FROM usuarios WHERE rol != 'Admin'")
    empleados = cur.fetchall()

    if request.method == 'POST':
        # Seguridad adicional por si alguien intenta postear manualmente
        if tarea['estado'] == 'Realizada':
            flash("⚠️ Esta tarea ya está marcada como realizada y no puede editarse", "warning")
            return redirect(url_for('tareas.listar_tareas'))

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


# =====================================================
# ELIMINAR TAREA
# =====================================================
@tareas.route('/tareas/eliminar/<int:id>')
def eliminar_tarea(id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM tareas WHERE idTarea = %s", (id,))
    conn.commit()

    cur.close()
    conn.close()
    flash("🗑️ Tarea eliminada correctamente", "info")
    return redirect(url_for('tareas.listar_tareas'))


# =====================================================
# LISTAR TAREAS PENDIENTES
# =====================================================
@tareas.route('/tareas/pendientes')
def tareas_pendientes():
    id_usuario = session["idUsuario"]

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT t.idTarea, t.nombreTarea, t.descripcion, t.prioridad, 
               t.fechaInicio, t.fechaFin, t.estado,
               u.nombre AS empleado
        FROM tareas t
        JOIN usuarios u ON t.idUsuario = u.idUsuario
        WHERE t.estado = 'Pendiente' AND u.idUsuario = %s
    """, (id_usuario,))
    pendientes = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('tareas_pendientes.html', pendientes=pendientes)


# =====================================================
# CAMBIAR ESTADO (REALIZADA / PENDIENTE)
# =====================================================
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

    
@tareas.route('/tareas/<int:id>')
def detalle_tarea(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            t.idTarea, t.nombreTarea, t.descripcion, t.prioridad,
            t.fechaInicio, t.fechaFin, t.estado,
            u.nombre AS empleado
        FROM tareas t
        JOIN usuarios u ON t.idUsuario = u.idUsuario
        WHERE t.idTarea = %s
    """, (id,))
    
    tarea = cursor.fetchone()

    cursor.close()
    conn.close()

    if not tarea:
        flash("La tarea no existe", "danger")
        return redirect(url_for('tareas.listar_tareas'))

    return render_template('detalle_tarea.html', tarea=tarea)



