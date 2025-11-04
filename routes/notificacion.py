from flask import Blueprint, request, jsonify, session
from db import get_connection


notificaciones_bp = Blueprint('notificaciones', __name__)

# 🔄 Obtener roles (menos Admin)
@notificaciones_bp.route('/roles_notificacion')
def roles_notificacion():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT rol FROM usuarios WHERE rol != 'Admin'")
    roles = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(roles)

# 🔄 Obtener usuarios por rol
@notificaciones_bp.route('/usuarios_por_rol/<rol>')
def usuarios_por_rol(rol):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idUsuario, nombre, apellido FROM usuarios WHERE rol = %s", (rol,))
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(usuarios)

# 📩 Guardar notificación
@notificaciones_bp.route('/guardar_notificacion', methods=['POST'])
def guardar_notificacion():
    data = request.json
    titulo = data.get('titulo')
    descripcion = data.get('descripcion')
    idUsuario = data.get('idUsuario')
    rol = data.get('rol')

    if not all([titulo, descripcion, idUsuario, rol]):
        return jsonify({'error': 'Faltan datos'}), 400

    try:
        idUsuario = int(idUsuario)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notificacion (idUsuario, titulo, rol, descripcion, fecha, leida)
            VALUES (%s, %s, %s, %s, NOW(), 0)
        """, (idUsuario, titulo, rol, descripcion))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print("Error en MySQL:", e)
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cur.close()
        conn.close()

# ✅ Marcar notificación como leída
@notificaciones_bp.route('/marcar_notificacion/<int:id>', methods=['POST'])
def marcar_notificacion(id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE notificacion SET leida = 1 WHERE id = %s", (id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print("Error al marcar notificación:", e)
        return jsonify({'success': False, 'error': str(e)})
    finally:
        cur.close()
        conn.close()

# 🔄 Obtener todas las notificaciones del usuario actual
@notificaciones_bp.route('/mis_notificaciones')
def mis_notificaciones():
    # Aquí debes obtener el idUsuario de la sesión
    id_usuario = session.get('idUsuario')  # Asumiendo que guardas el usuario en session

    if not id_usuario:
        return jsonify([])  # No hay usuario logueado

    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, titulo, descripcion, rol, fecha, leida
            FROM notificacion
            WHERE idUsuario = %s
            ORDER BY fecha DESC
        """, (id_usuario,))
        notis = cur.fetchall()
        return jsonify(notis)
    except Exception as e:
        print("Error al obtener notificaciones:", e)
        return jsonify([])
    finally:
        cur.close()
        conn.close()