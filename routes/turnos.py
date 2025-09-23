from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection  # tu función de conexión

turnos_bp = Blueprint("turnos_bp", __name__)

# Página principal que muestra todos los turnos asignados
@turnos_bp.route("/horarios", methods=["GET"])
def horarios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            ut.id,
            u.nombre AS empleado,
            u.rol AS area,
            CONCAT(h.horaInicio, ' - ', h.horaFin) AS turno
        FROM usuarioturno ut
        JOIN horariosyturnos h ON ut.idHorario = h.idHorario
        JOIN usuarios u ON ut.idUsuario = u.idUsuario
        WHERE ut.activo = 1
        ORDER BY ut.fechaInicio DESC
    """)
    asignaciones = cur.fetchall()

    # También traemos los turnos disponibles para el formulario de asignación
    cur.execute("SELECT * FROM horariosyturnos")
    turnos = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("horario.html", asignaciones=asignaciones, turnos=turnos)


# Crear un nuevo turno
@turnos_bp.route("/crear_turno", methods=["POST"])
def crear_turno():
    hora_inicio = request.form.get("horaInicio")
    hora_fin = request.form.get("horaFin")

    if not hora_inicio or not hora_fin:
        flash("Debes completar ambas horas")
        return redirect(url_for("turnos_bp.horarios"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO horariosyturnos (horaInicio, horaFin)
        VALUES (%s, %s)
    """, (hora_inicio, hora_fin))
    conn.commit()
    cur.close()
    conn.close()

    flash("Turno creado ✅")
    return redirect(url_for("turnos_bp.horarios"))


# Asignar un turno a un usuario
@turnos_bp.route("/asignar_turno", methods=["POST"])
def asignar_turno():
    id_usuario = request.form.get("usuario")
    id_horario = request.form.get("idHorario")
    fecha_inicio = request.form.get("fechaInicio")
    fecha_fin = request.form.get("fechaFin")

    if not all([id_usuario, id_horario, fecha_inicio, fecha_fin]):
        flash("Todos los campos son obligatorios")
        return redirect(url_for("turnos_bp.horarios"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarioturno (idHorario, idUsuario, fechaInicio, fechaFin, activo)
        VALUES (%s, %s, %s, %s, 1)
    """, (id_horario, id_usuario, fecha_inicio, fecha_fin))
    conn.commit()
    cur.close()
    conn.close()

    flash("Turno asignado ✅")
    return redirect(url_for("turnos_bp.horarios"))
