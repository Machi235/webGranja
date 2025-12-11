from datetime import datetime
from db import get_connection
from routes.notificacion import guardar_notificacion


def enviar(idUsuario, titulo, descripcion):
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
    print(">>> EJECUTANDO revisar_recordatorios()")

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    hoy = datetime.now().strftime("%Y-%m-%d")

    # Obtener destinatarios
    cur.execute("""
        SELECT idUsuario 
        FROM usuarios 
        WHERE rol IN ('Admin','Cuidador') AND activo = 1
    """)
    destinatarios = cur.fetchall()

    # 🔥 Unificar eventos con columnas reales
    cur.execute("""
        SELECT idAnimal, tipo, proximaFecha FROM (
            SELECT idAnimal, 'Cirugía' AS tipo, fechaCirugia AS proximaFecha 
            FROM cirugia
            UNION ALL
            SELECT idAnimal, 'Vacuna' AS tipo, proximaVacuna AS proximaFecha 
            FROM vacuna
            UNION ALL
            SELECT idAnimal, 'Visita veterinaria' AS tipo, proximaVisita AS proximaFecha 
            FROM visitas
            UNION ALL
            SELECT idAnimal, 'Terapia física' AS tipo, proximaSesion AS proximaFecha 
            FROM terapiafisica
            UNION ALL
            SELECT idAnimal, 'Medicación' AS tipo, horaSiguienteaplicacion AS proximaFecha 
            FROM medicacion
        ) AS eventos
        WHERE proximaFecha = %s
    """, (hoy,))

    eventos_hoy = cur.fetchall()

    if eventos_hoy:
        for evento in eventos_hoy:
            # Obtener nombre del animal
            cur.execute("SELECT nombre FROM animal WHERE idAnimal = %s", (evento["idAnimal"],))
            animal = cur.fetchone()

            titulo = f"Recordatorio: {evento['tipo']}"
            descripcion = (
                f"Hoy corresponde el evento '{evento['tipo']}' para el animal "
                f"{animal['nombre'] if animal else evento['idAnimal']}."
            )

            for d in destinatarios:
                enviar(d['idUsuario'], titulo, descripcion)

    conn.close()
