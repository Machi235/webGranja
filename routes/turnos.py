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
            ut.idUsuarioturno,
            u.nombre, 
            u.apellido,
            u.rol AS area,
            h.idHorario,
            h.nombreTurno AS turno
        FROM usuarioturno ut
        JOIN horariosturnos h ON ut.idHorario = h.idHorario
        JOIN usuarios u ON ut.idUsuario = u.idUsuario
        WHERE u.activo = 1
        ORDER BY h.nombreTurno DESC
    """)
    asignaciones = cur.fetchall()

    #Traemos los turnos disponibles para el formulario de asignación
    cur.execute("SELECT * FROM horariosturnos WHERE activo = 1")
    turnos = cur.fetchall()

    #Trae todos los usuarios que no tengan un horario y que su rol no sea de admnistrador
    cur.execute("SELECT u.idUsuario, nombre, apellido FROM usuarios AS u LEFT JOIN usuarioturno AS t ON u.idUsuario = t.idUsuario WHERE t.idUsuario IS NULL AND rol != 'Admin';")      
    usuarios = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("horario.html", asignaciones=asignaciones, turnos=turnos, usuarios=usuarios)


# Crear un nuevo turno
@turnos_bp.route("/crear_turno", methods=["POST"])
def crear_turno():
    nombre_turno = request.form.get("nombreTurno")
    hora_inicio = request.form.get("horaInicio")
    hora_fin = request.form.get("horaFin")

    if not hora_inicio or not hora_fin or not nombre_turno:
        flash("Debes completar todos los campos")
        return redirect(url_for("turnos_bp.horarios"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO horariosturnos (nombreTurno, horaInicio, horaFin)
        VALUES (%s, %s, %s)
    """, (nombre_turno, hora_inicio, hora_fin ))
    conn.commit()
    cur.close()
    conn.close()

    flash("Turno creado")
    return redirect(url_for("turnos_bp.horarios"))


# Asignar un turno a un usuario
@turnos_bp.route("/asignar_turno", methods=["POST"])
def asignar_turno():
    id_usuario = request.form.get("idUsuario")
    id_horario = request.form.get("idHorario")


    if not all([id_usuario, id_horario]):
        flash("Todos los campos son obligatorios")
        return redirect(url_for("turnos_bp.horarios"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarioturno (idHorario, idUsuario)
        VALUES (%s, %s)
    """, (id_horario, id_usuario))
    conn.commit()
    cur.close()
    conn.close()

    flash("Turno asignado")
    return redirect(url_for("turnos_bp.horarios"))

#Actualizar asigancion de turno 
@turnos_bp.route("/actualizar_asignar_turno", methods=["POST"])
def actualizar_asignar_turno():
    idUsuarioturno = request.form.get("idUsuarioturno")
    idHorario = request.form.get("idHorario")


    if not all([idUsuarioturno, idHorario]):
        flash("Todos los campos son obligatorios")
        return redirect(url_for("turnos_bp.horarios"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE usuarioturno SET idHorario = %s WHERE idUsuarioturno = %s
    """, (idHorario, idUsuarioturno))
    
    conn.commit()
    cur.close()
    conn.close()

    flash("Turno actualizado")
    return redirect(url_for("turnos_bp.horarios"))

@turnos_bp.route("/eliminar_turno/<int:idHorario>", methods=["POST"])
def eliminar_turno(idHorario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE horariosturnos SET activo = 0 WHERE idHorario =%s",(idHorario,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("turnos_bp.horarios"))
