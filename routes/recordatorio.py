from datetime import datetime
from db import get_connection
from routes.notificacion import guardar_notificacion


def enviar(idUsuario, titulo, descripcion):
    """
    Helper para insertar notificaciones.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO notificacion (idUsuario, titulo, descripcion, fecha, leida)
        VALUES (%s, %s, %s, NOW(), 0)
    """, (idUsuario, titulo, descripcion))
    conn.commit()
    cur.close()
    conn.close()


def revisar_recordatorios():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    hoy = datetime.now().strftime("%Y-%m-%d")

    # Roles que deben recibir recordatorios
    cur.execute("SELECT idUsuario FROM usuarios WHERE rol IN ('Admin','Cuidador') AND activo = 1")
    destinatarios = cur.fetchall()

    # Eventos clínicos con recordatorio
    cur.execute("""
        SELECT ec.idAnimal, a.nombre AS animal, ec.tipo, ec.descripcion, ec.proximaFecha
        FROM eventosclinicos ec
        INNER JOIN animal a ON ec.idAnimal = a.idAnimal
        WHERE ec.proximaFecha = %s
    """, (hoy,))

    eventos_hoy = cur.fetchall()

    if eventos_hoy:
        for evento in eventos_hoy:
            titulo = f"Recordatorio: {evento['tipo']}"
            descripcion = f"Hoy corresponde el evento '{evento['tipo']}' para el animal {evento['animal']}."

            for d in destinatarios:
                enviar(d['idUsuario'], titulo, descripcion)

    conn.close()
