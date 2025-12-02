
import os
from flask import Blueprint, make_response, render_template, request, redirect, url_for, flash
from db import get_connection  # tu función de conexión
from io import BytesIO #Modulo de entradas y salidas
from reportlab.lib.pagesizes import letter #tamaño de papel
from reportlab.lib.styles import getSampleStyleSheet #Estilos de texto
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer #Contenido de pdf
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection

turnos_bp = Blueprint("turnos_bp", __name__)


# ================================
#   MOSTRAR HORARIOS
# ================================
@turnos_bp.route("/horarios", methods=["GET"])
def horarios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Asignaciones mostradas en la tabla grande
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

    # Turnos para los formularios
    cur.execute("SELECT * FROM horariosturnos WHERE activo = 1")
    turnos = cur.fetchall()

    # Usuarios que aún no tienen turno asignado
    cur.execute("""
        SELECT u.idUsuario, nombre, apellido 
        FROM usuarios AS u 
        LEFT JOIN usuarioturno AS t ON u.idUsuario = t.idUsuario 
        WHERE t.idUsuario IS NULL AND rol != 'Admin';
    """)
    usuarios = cur.fetchall()

    # Notificaciones del admin
    notificaciones, no_leidas = [], 0
    if "idUsuario" in session:
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session['idUsuario'],))
        notificaciones = cur.fetchall()
        no_leidas = sum(1 for n in notificaciones if not n.get("leida"))

    cur.close()
    conn.close()

    return render_template(
        "horario.html",
        asignaciones=asignaciones,
        turnos=turnos,
        usuarios=usuarios,
        notificaciones=notificaciones,
        notificaciones_no_leidas=no_leidas,
        rol=session.get("rol")
    )


# ================================
#   CREAR NUEVO TURNO
# ================================
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
    """, (nombre_turno, hora_inicio, hora_fin))
    conn.commit()
    cur.close()
    conn.close()

    flash("Turno creado correctamente")
    return redirect(url_for("turnos_bp.horarios"))


# ================================
#   ASIGNAR TURNO NORMAL
# ================================
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

    flash("Turno asignado correctamente")
    return redirect(url_for("turnos_bp.horarios"))


# ========================================================
#   NUEVO: ENVIAR SOLICITUD A ADMIN AL EDITAR UN TURNO
# ========================================================
@turnos_bp.route("/actualizar_asignar_turno", methods=["POST"])
def actualizar_asignar_turno():

    idUsuarioturno = request.form.get("idUsuarioturno")
    idHorarioNuevo = request.form.get("idHorario")

    if not all([idUsuarioturno, idHorarioNuevo]):
        flash("Todos los campos son obligatorios")
        return redirect(url_for("turnos_bp.horarios"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Obtener info para notificación
    cur.execute("""
        SELECT ut.idUsuario, u.nombre, u.apellido, h.nombreTurno AS turnoActual
        FROM usuarioturno ut
        JOIN usuarios u ON ut.idUsuario = u.idUsuario
        JOIN horariosturnos h ON ut.idHorario = h.idHorario
        WHERE ut.idUsuarioturno = %s
    """, (idUsuarioturno,))
    datos = cur.fetchone()

    # Obtener nombre del turno nuevo
    cur.execute("SELECT nombreTurno FROM horariosturnos WHERE idHorario = %s", (idHorarioNuevo,))
    turno_nuevo = cur.fetchone()["nombreTurno"]

    # -----------------------------------------------------------
    # 🔥 NUEVA DESCRIPCIÓN COMPLETA Y CORRECTA
    # -----------------------------------------------------------
    descripcion = (
        f"CambioTurno |{datos['idUsuario']}|{idUsuarioturno}|{idHorarioNuevo}|"
        f"{datos['nombre']} {datos['apellido']} solicita cambiar de {datos['turnoActual']} a {turno_nuevo}"
    )

    # Crear notificación para el admin (idUsuario = 1)
    cur.execute("""
        INSERT INTO notificacion (idUsuario, titulo, rol, descripcion, fecha, leida)
        VALUES (%s, %s, %s, %s, NOW(), 0)
    """, (
        1,
        "Solicitud de cambio de turno",
        "Admin",
        descripcion
    ))

    conn.commit()
    cur.close()
    conn.close()

    flash("Solicitud enviada al administrador. Espera su aprobación.")
    return redirect(url_for("turnos_bp.horarios"))



# ========================================================
#   RUTA PARA APROBAR O RECHAZAR SOLICITUD
# ========================================================
@turnos_bp.route("/resolver_cambio/<int:idNotificacion>/<string:accion>")
def resolver_cambio(idNotificacion, accion):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Leer notificación
    cur.execute("SELECT descripcion FROM notificacion WHERE id = %s", (idNotificacion,))
    data = cur.fetchone()["descripcion"]

    partes = data.split("|")
    print("DEBUG DESCRIPCION:", data)
    print("DEBUG PARTES:", partes)


    # --- VALIDACIÓN DE SEGURIDAD ---
    if len(partes) < 4:
        # No es un cambio de turno → solo marcar como leída
        cur.execute("UPDATE notificacion SET leida = 1 WHERE id = %s", (idNotificacion,))
        conn.commit()
        flash("Notificación procesada.")
        cur.close()
        conn.close()
        return redirect(url_for("turnos_bp.horarios"))

    # Extraer valores SOLO si la notificación es válida
    idUsuarioturno = partes[2]
    idHorarioNuevo = partes[3]

    # Acción
    if accion == "si":
        cur.execute("""
            UPDATE usuarioturno 
            SET idHorario = %s 
            WHERE idUsuarioturno = %s
        """, (idHorarioNuevo, idUsuarioturno))
        mensaje = "Cambio de turno aprobado"
    else:
        mensaje = "Solicitud rechazada"

    # Marcar notificación como leída
    cur.execute("UPDATE notificacion SET leida = 1 WHERE id = %s", (idNotificacion,))
    conn.commit()

    cur.close()
    conn.close()

    flash(mensaje)
    return redirect(url_for("turnos_bp.horarios"))



# ================================
#   ELIMINAR TURNO
# ================================
@turnos_bp.route("/eliminar_turno/<int:idHorario>", methods=["POST"])
def eliminar_turno(idHorario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE horariosturnos SET activo = 0 WHERE idHorario = %s", (idHorario,))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for("turnos_bp.horarios"))

@turnos_bp.route("/pdf_horarios")
def generar_pdf():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT 
            u.nombre, 
            u.apellido,
            u.rol AS area,
            h.nombreTurno AS turno
        FROM usuarioturno ut
        JOIN horariosturnos h ON ut.idHorario = h.idHorario
        JOIN usuarios u ON ut.idUsuario = u.idUsuario
        WHERE u.activo = 1
        ORDER BY h.nombreTurno DESC
    """)
    asignaciones = cur.fetchall()

    buffer = BytesIO() #Crea un espacio temporal en memoria
    pdf = SimpleDocTemplate(buffer, pagesize=letter) #Se crea el documento pdf
    elements = [] #Lista vacia donde se pone el contenido
    styles = getSampleStyleSheet() #conjunto de estilos 

    elements.append(Paragraph(f"<b>Turnos</b>", styles["Title"])) #Agrgar un parrafro al pdf

    datos = [["Nombre", "Apellido", "Area", "Turno"]]

    for fila in asignaciones:
        datos.append([
            fila["nombre"],
            fila["apellido"],
            fila["area"],
            fila["turno"],
        ])
    
    tabla = Table(datos, colWidths=[100,100,100,100])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),

        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("BACKGROUND", (0,1), (-1,-1), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(Spacer(1, 20)) #Pie de pagina
    elements.append(tabla)


    pdf.build(elements) #Crea el pdf con todos elementos en el mismo orden  

    response = make_response(buffer.getvalue()) # sE crea una respuesta http con los bytes obtenidos en el buffer    
    response.headers["Content-Type"] = "application/pdf" #Dice que el contenido es un pdf
    response.headers["Content-Disposition"] = "inline; filename=animal.pdf" #Lo abre directamente
    return response 