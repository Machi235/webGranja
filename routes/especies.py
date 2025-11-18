from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db import get_connection

especies_bp = Blueprint('especies_bp', __name__)

def obtener_notificaciones(user_id):
    """Función ejemplo para obtener notificaciones"""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM notificacion WHERE idUsuario=%s ORDER BY fecha DESC", (user_id,))
    notificaciones = cur.fetchall()
    cur.execute("SELECT COUNT(*) AS total_no_leidas FROM notificacion WHERE idUsuario=%s AND leida=0", (user_id,))
    notificaciones_no_leidas = cur.fetchone()['total_no_leidas']
    conn.close()
    return notificaciones, notificaciones_no_leidas

# Ver todas las especies
@especies_bp.route('/especies')
def ver_especies():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM especie ORDER BY idEspecie")
    especies = cur.fetchall()
    conn.close()

    # Obtener notificaciones y rol
    rol = session.get('rol')
    user_id = session.get('idUsuario')  # Asumiendo que guardas el idUsuario en session
    notificaciones, notificaciones_no_leidas = obtener_notificaciones(user_id)

    return render_template(
        'especies.html',
        especies=especies,
        rol=rol,
        notificaciones=notificaciones,
        notificaciones_no_leidas=notificaciones_no_leidas
    )

# Registrar nueva especie
@especies_bp.route('/especies', methods=['POST'])
def registrar_especie():
    tipo = request.form.get('tipoEspecie')
    limite = request.form.get('limite')
    periodo = request.form.get('periodo')

    if tipo and limite and periodo:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO especie (tipoEspecie, limite, periodo) VALUES (%s, %s, %s)", 
                    (tipo, limite, periodo))
        conn.commit()
        conn.close()
        flash('Especie agregada correctamente', 'success')
    else:
        flash('Todos los campos son obligatorios', 'danger')

    return redirect(url_for('especies_bp.ver_especies'))

# Editar especie
@especies_bp.route('/especies/editar/<int:idEspecie>', methods=['GET', 'POST'])
def editar_especie(idEspecie):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        tipo = request.form.get('tipoEspecie')
        limite = request.form.get('limite')
        periodo = request.form.get('periodo')

        cur.execute("UPDATE especie SET tipoEspecie=%s, limite=%s, periodo=%s WHERE idEspecie=%s",
                    (tipo, limite, periodo, idEspecie))
        conn.commit()
        conn.close()
        flash('Especie actualizada', 'success')
        return redirect(url_for('especies_bp.ver_especies'))

    cur.execute("SELECT * FROM especie WHERE idEspecie=%s", (idEspecie,))
    especie = cur.fetchone()
    conn.close()

    # Notificaciones y rol
    rol = session.get('rol')
    user_id = session.get('idUsuario')
    notificaciones, notificaciones_no_leidas = obtener_notificaciones(user_id)

    return render_template(
        'editar_especie.html',
        especie=especie,
        rol=rol,
        notificaciones=notificaciones,
        notificaciones_no_leidas=notificaciones_no_leidas
    )

# Eliminar especie
@especies_bp.route('/especies/eliminar/<int:idEspecie>')
def eliminar_especie(idEspecie):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM especie WHERE idEspecie=%s", (idEspecie,))
    conn.commit()
    conn.close()
    flash('Especie eliminada', 'success')
    return redirect(url_for('especies_bp.ver_especies'))
