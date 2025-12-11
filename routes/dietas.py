import os
from flask import Blueprint, make_response, render_template, request, jsonify, session
from db import get_connection
from datetime import datetime
from io import BytesIO #Modulo de entradas y salidas
from reportlab.lib.pagesizes import letter #tamaño de papel
from reportlab.lib.styles import getSampleStyleSheet #Estilos de texto
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image #Contenido de pdf
from reportlab.lib.units import cm #Usar unidades de medida 

dietas = Blueprint("dietas", __name__)

# =========================================================
#           CREAR DIETA
# =========================================================
@dietas.route("/crear_dieta", methods=["GET", "POST"])
def crear_dieta():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        if request.method == "POST":
            idEspecie = request.form.get("idEspecie")
            descripcion = request.form.get("descripcion")
            definitivo = 1 if request.form.get("definitivo") else 0
            idCuidador = request.form.get("idCuidador")
            horaDieta = request.form.get("horaDieta")

            # Insertar dieta
            cur.execute("""
                        INSERT INTO dieta (idEspecie, descripcion, definitivo, horaDieta, idCuidador)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (idEspecie, descripcion, definitivo, horaDieta, idCuidador))

            idDieta = cur.lastrowid

            # Guardar alimentos
            idAlimentos = request.form.getlist("idAlimento[]")
            cantidades = request.form.getlist("cantidadAlimento[]")
            frecuencias = request.form.getlist("frecuenciaAlimento[]")

            for i in range(len(idAlimentos)):
                cur.execute("""
                    INSERT INTO dietaalimento (idDieta, idAlimento, cantidadAlimento, frecuenciaAlimento)
                    VALUES (%s, %s, %s, %s)
                """, (idDieta, idAlimentos[i], cantidades[i], frecuencias[i]))

            # Obtener nombre de la especie para la notificación
            cur.execute("SELECT tipoEspecie FROM especie WHERE idEspecie = %s", (idEspecie,))
            especie_row = cur.fetchone()
            nombre_especie = especie_row["tipoEspecie"] if especie_row else "Especie desconocida"

            # Crear notificaciones
            cur.execute("SELECT idUsuario FROM usuarios WHERE rol IN ('Admin','Cuidador') AND activo=1")
            destinatarios = cur.fetchall()
            titulo = "Nueva Dieta Registrada"
            desc_notif = f"Se registró una dieta para la especie: {nombre_especie}"
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for d in destinatarios:
                cur.execute("""
                    INSERT INTO notificacion (idUsuario, titulo, descripcion, fecha, leida)
                    VALUES (%s, %s, %s, %s, 0)
                """, (d["idUsuario"], titulo, desc_notif, fecha_actual))

            conn.commit()
            return jsonify({"success": True})

        # GET
        cur.execute("SELECT idEspecie, tipoEspecie FROM especie ORDER BY tipoEspecie")
        especies = cur.fetchall()

        rol = session.get("rol")
        notificaciones = []
        notificaciones_no_leidas = 0
        if "idUsuario" in session:
            cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session["idUsuario"],))
            notificaciones = cur.fetchall()
            notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get("leida"))
            
        cur.execute("""
                    SELECT idUsuario, nombre, apellido
                    FROM usuarios
                    WHERE rol = 'Cuidador' AND activo = 1
                """)
        cuidadores = cur.fetchall()

        return render_template(
            "crearDieta.html",
            especies=especies,
            cuidadores=cuidadores,
            rol=rol,
            notificaciones=notificaciones,
            notificaciones_no_leidas=notificaciones_no_leidas
        )

    except Exception as e:
        print("ERROR crear_dieta:", e)
        return jsonify({"success": False, "error": str(e)})

    finally:
        cur.close()
        conn.close()

# =========================================================
#           VER DIETAS
# =========================================================
@dietas.route("/ver_dietas", methods=["GET"])
def ver_dietas():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # --------------- PAGINACIÓN ---------------
        pagina = request.args.get("page", default=1, type=int)
        limite = 6  # dietas por página
        offset = (pagina - 1) * limite

        # --------------- FILTRO POR ESPECIE ---------------
        idEspecie_filtro = request.args.get("idEspecie", type=int)

        # Primero contar cuántas dietas hay (para calcular total paginado)
        sql_count = """
            SELECT COUNT(*) AS total
            FROM dieta d
        """
        params = ()

        if idEspecie_filtro:
            sql_count += " WHERE d.idEspecie = %s"
            params = (idEspecie_filtro,)

        cur.execute(sql_count, params)
        total_registros = cur.fetchone()["total"]
        total_paginas = (total_registros + limite - 1) // limite

        # --------------- OBTENER DIETAS PAGINADAS ---------------
        sql = """
            SELECT
                d.idDieta,
                d.descripcion AS tipoDieta,
                d.definitivo,
                d.fechaRegistro,
                e.idEspecie,
                e.tipoEspecie,
                da.idAlimento,
                al.Origen AS nombreAlimento,
                da.cantidadAlimento,
                da.frecuenciaAlimento
            FROM dieta d
            JOIN especie e ON d.idEspecie = e.idEspecie
            LEFT JOIN dietaalimento da ON d.idDieta = da.idDieta
            LEFT JOIN alimento al ON da.idAlimento = al.idAlimento
        """

        if idEspecie_filtro:
            sql += " WHERE d.idEspecie = %s"
            sql += " ORDER BY d.idDieta DESC LIMIT %s OFFSET %s"
            params = (idEspecie_filtro, limite, offset)
        else:
            sql += " ORDER BY d.idDieta DESC LIMIT %s OFFSET %s"
            params = (limite, offset)

        cur.execute(sql, params)
        rows = cur.fetchall()

        # Agrupar dietas
        dietas_dict = {}
        for row in rows:
            idDieta = row["idDieta"]
            if idDieta not in dietas_dict:
                dietas_dict[idDieta] = {
                    "idDieta": idDieta,
                    "tipoDieta": row["tipoDieta"],
                    "definitivo": row["definitivo"],
                    "fechaRegistro": row.get("fechaRegistro"),
                    "idEspecie": row["idEspecie"],
                    "tipoEspecie": row["tipoEspecie"],
                    "alimentos": []
                }
            if row.get("idAlimento"):
                dietas_dict[idDieta]["alimentos"].append({
                    "idAlimento": row.get("idAlimento"),
                    "nombreAlimento": row.get("nombreAlimento"),
                    "cantidadAlimento": row.get("cantidadAlimento"),
                    "frecuenciaAlimento": row.get("frecuenciaAlimento")
                })

        dietas_list = list(dietas_dict.values())

        # Filtro especies
        cur.execute("SELECT idEspecie, tipoEspecie FROM especie ORDER BY tipoEspecie")
        especies = cur.fetchall()

        # Datos nav
        rol = session.get("rol")
        notificaciones = []
        notificaciones_no_leidas = 0
        if "idUsuario" in session:
            cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session["idUsuario"],))
            notificaciones = cur.fetchall()
            notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get("leida"))

        return render_template(
            "verDietas.html",
            dietas=dietas_list,
            especies=especies,
            rol=rol,
            notificaciones=notificaciones,
            notificaciones_no_leidas=notificaciones_no_leidas,
            filtro_idEspecie=idEspecie_filtro,
            pagina=pagina,
            total_paginas=total_paginas
        )

    except Exception as e:
        print("ERROR ver_dietas:", e)
        return jsonify({"error": "Ocurrió un error al cargar las dietas"}), 500

    finally:
        cur.close()
        conn.close()


# =========================================================
#           ALIMENTOS POR ESPECIE
# =========================================================
@dietas.route("/alimentos_por_especie/<int:idEspecie>", methods=["GET"])
def alimentos_por_especie(idEspecie):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT idAlimento, Origen FROM alimento WHERE idEspecie=%s ORDER BY Origen", (idEspecie,))
        alimentos = cur.fetchall()
        return jsonify({"success": True, "alimentos": alimentos})
    except Exception as e:
        print("ERROR alimentos_por_especie:", e)
        return jsonify({"success": False, "error": str(e)})
    finally:
        cur.close()
        conn.close()

@dietas.route("/eliminar_dieta/<int:idDieta>", methods=["POST"])
def eliminar_dieta(idDieta):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # Primero eliminamos los alimentos asociados
        cur.execute("DELETE FROM dietaalimento WHERE idDieta=%s", (idDieta,))
        # Luego eliminamos la dieta
        cur.execute("DELETE FROM dieta WHERE idDieta=%s", (idDieta,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("ERROR eliminar_dieta:", e)
        return jsonify({"success": False, "error": str(e)})
    finally:
        cur.close()
        conn.close()

@dietas.route("/editar_dieta/<int:idDieta>", methods=["GET", "POST"])
def editar_dieta(idDieta):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        if request.method == "POST":
            idEspecie = request.form.get("idEspecie")
            descripcion = request.form.get("descripcion")
            definitivo = 1 if request.form.get("definitivo") else 0

            # Actualizar dieta
            cur.execute("""
                UPDATE dieta
                SET idEspecie = %s, descripcion = %s, definitivo = %s
                WHERE idDieta = %s
            """, (idEspecie, descripcion, definitivo, idDieta))

            # Eliminar alimentos antiguos
            cur.execute("DELETE FROM dietaalimento WHERE idDieta = %s", (idDieta,))

            # Insertar nuevos alimentos
            idAlimentos = request.form.getlist("idAlimento[]")
            cantidades = request.form.getlist("cantidadAlimento[]")
            frecuencias = request.form.getlist("frecuenciaAlimento[]")

            for i in range(len(idAlimentos)):
                cur.execute("""
                    INSERT INTO dietaalimento (idDieta, idAlimento, cantidadAlimento, frecuenciaAlimento)
                    VALUES (%s, %s, %s, %s)
                """, (idDieta, idAlimentos[i], cantidades[i], frecuencias[i]))

            conn.commit()
            return jsonify({"success": True})

        # ================= GET =================
        # Obtener dieta
        cur.execute("SELECT * FROM dieta WHERE idDieta = %s", (idDieta,))
        dieta = cur.fetchone()
        if not dieta:
            return "Dieta no encontrada", 404

        # Obtener especies
        cur.execute("SELECT idEspecie, tipoEspecie FROM especie ORDER BY tipoEspecie")
        especies = cur.fetchall()

        # Obtener alimentos de la dieta
        cur.execute("""
            SELECT da.idAlimento, al.Origen AS nombre, da.cantidadAlimento, da.frecuenciaAlimento
            FROM dietaalimento da
            JOIN alimento al ON da.idAlimento = al.idAlimento
            WHERE da.idDieta = %s
        """, (idDieta,))
        alimentos_raw = cur.fetchall() or []
        alimentos = []
        for a in alimentos_raw:
            alimentos.append({
                "idAlimento": int(a["idAlimento"]),
                "nombre": str(a["nombre"]),
                "cantidadAlimento": str(a["cantidadAlimento"]),
                "frecuenciaAlimento": str(a["frecuenciaAlimento"])
            })

        # Obtener todos los alimentos disponibles para la especie
        cur.execute("""
            SELECT idAlimento, Origen AS nombre
            FROM alimento
            WHERE idEspecie = %s
        """, (dieta['idEspecie'],))
        alimentos_disponibles_raw = cur.fetchall() or []
        alimentosDisponibles = []
        for a in alimentos_disponibles_raw:
            alimentosDisponibles.append({
                "idAlimento": int(a["idAlimento"]),
                "nombre": str(a["nombre"])
            })

        # Datos para nav
        rol = session.get("rol")
        notificaciones = []
        notificaciones_no_leidas = 0
        if "idUsuario" in session:
            cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session["idUsuario"],))
            notificaciones = cur.fetchall()
            notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get("leida"))
        
        # Si no hay alimentos, usar lista vacía
        alimentos = alimentos if alimentos else []
        alimentosDisponibles = alimentosDisponibles if alimentosDisponibles else []


        return render_template(
            "editarDieta.html",
            dieta=dieta,
            especies=especies,
            alimentos=alimentos,
            alimentosDisponibles=alimentosDisponibles,
            rol=rol,
            notificaciones=notificaciones,
            notificaciones_no_leidas=notificaciones_no_leidas
        )

    except Exception as e:
        print("ERROR editar_dieta:", e)
        return jsonify({"error": str(e)})

    finally:
        cur.close()
        conn.close()

@dietas.route("/pdf_dieta<int:idDieta>")
def generar_pdf(idDieta):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
            SELECT
                d.idDieta,
                d.descripcion AS tipoDieta,
                d.definitivo,
                d.fechaRegistro,
                e.idEspecie,
                e.tipoEspecie,
                da.idAlimento,
                al.Origen AS nombreAlimento,
                da.cantidadAlimento,
                da.frecuenciaAlimento
            FROM dieta d
            JOIN especie e ON d.idEspecie = e.idEspecie
            LEFT JOIN dietaalimento da ON d.idDieta = da.idDieta
            LEFT JOIN alimento al ON da.idAlimento = al.idAlimento
            WHERE d.idDieta = %s
    """, (idDieta,))
    dieta = cur.fetchone()

    buffer = BytesIO() #Crea un espacio temporal en memoria
    pdf = SimpleDocTemplate(buffer, pagesize=letter) #Se crea el documento pdf
    elements = [] #Lista vacia donde se pone el contenido
    styles = getSampleStyleSheet() #conjunto de estilos 

    elements.append(Paragraph(f"<b>Dieta por especie</b>", styles["Title"])) #Agrgar un parrafro al pdf
    elements.append(Spacer(1,12)) #Inserta un espacio entre cada elemento 

    contenido = f"""
    <b>Especie o animal:</b>{dieta['tipoEspecie']}<br/>
    <b>Tipo de dieta:</b>{dieta['tipoDieta']}<br/>
    <b>Alimento:</b>{dieta['nombreAlimento']}<br/>
    <b>Cantidad:</b>{dieta['cantidadAlimento']}<br/>
    <b>Frecuencia:</b>{dieta['frecuenciaAlimento']}<br/>"""

    elements.append(Spacer(1,12)) 

    styles = getSampleStyleSheet()
    estilo_grande = styles["Normal"].clone('estilo_grande')
    estilo_grande.fontSize = 14   # tamaño de letra
    estilo_grande.leading = 45    # espacio entre líneas

    elements.append(Paragraph(contenido, estilo_grande))

    elements.append(Spacer(1, 20)) #Pie de pagina

    pdf.build(elements) #Crea el pdf con todos elementos en el mismo orden  

    response = make_response(buffer.getvalue()) # sE crea una respuesta http con los bytes obtenidos en el buffer    
    response.headers["Content-Type"] = "application/pdf" #Dice que el contenido es un pdf
    response.headers["Content-Disposition"] = "inline; filename=animal.pdf" #Lo abre directamente
    return response 

@dietas.route("/check_dietas")
def check_dietas():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT d.idDieta, d.descripcion, d.horaDieta, d.idCuidador, e.tipoEspecie
        FROM dieta d
        JOIN especie e ON d.idEspecie = e.idEspecie
        WHERE d.horaDieta IS NOT NULL
          AND d.notificada = 0
          AND TIME(d.horaDieta) <= TIME(NOW())
    """)
    dietas = cur.fetchall()

    for d in dietas:
        cur.execute("""
            INSERT INTO notificacion (idUsuario, titulo, descripcion, fecha, leida)
            VALUES (%s, %s, %s, NOW(), 0)
        """, (
            d["idCuidador"],
            "Confirmar alimentación",
            f"Dieta {d['descripcion']} de especie {d['tipoEspecie']} — ¿El animal comió? |{d['idDieta']}",
        ))

        cur.execute("UPDATE dieta SET notificada = 1 WHERE idDieta=%s", (d["idDieta"],))

    conn.commit()
    return jsonify({"success": True})

@dietas.route("/responder_comida/<int:idNoti>/<string:respuesta>")
def responder_comida(idNoti, respuesta):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # 1. Obtener ID de la dieta desde la notificación original
    cur.execute("SELECT descripcion FROM notificacion WHERE id=%s", (idNoti,))
    row = cur.fetchone()

    if not row:
        return jsonify({"success": False, "error": "Notificación no encontrada"})

    desc = row["descripcion"]

    try:
        idDieta = desc.split("|")[1]  # Extrae ID de dieta
    except:
        return jsonify({"success": False, "error": "Descripción inválida"})

    # 2. Determinar si comió
    comio = 1 if respuesta == "si" else 0

    # 3. Obtener descripción REAL de la dieta
    cur.execute("SELECT descripcion FROM dieta WHERE idDieta = %s", (idDieta,))
    row_dieta = cur.fetchone()
    descripcion_dieta = row_dieta["descripcion"] if row_dieta else "Dieta sin descripción"

    # 4. Registrar historial
    cur.execute("""
        INSERT INTO dieta_historial (idDieta, fecha, hora, comio, idCuidador)
        VALUES (%s, CURDATE(), CURTIME(), %s, %s)
    """, (idDieta, comio, session["idUsuario"]))

    # 5. SI NO comió → notificar a TODOS los admins pero con DESCRIPCIÓN
    if not comio:

        cur.execute("SELECT idUsuario FROM usuarios WHERE rol = 'Admin'")
        admins = cur.fetchall()

        for admin in admins:
            cur.execute("""
                INSERT INTO notificacion (idUsuario, titulo, descripcion, fecha, leida)
                VALUES (%s, 'Alerta: Dieta no consumida',
                        %s, NOW(), 0)
            """, (admin["idUsuario"], f"El animal NO comió la dieta: {descripcion_dieta}"))

    # 6. Marcar notificación como leída
    cur.execute("UPDATE notificacion SET leida=1 WHERE id=%s", (idNoti,))

    conn.commit()
    return jsonify({"success": True})

# ======================================================================
#      CHECK AUTOMÁTICO (scheduler) - SE EJECUTA CADA 1 MINUTO
# ======================================================================
def check_dietas_background(app):
    with app.app_context():
        print("CHECK DIETAS EJECUTADO", datetime.now())

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Buscar dietas cuya hora YA pasó y que NO han sido notificadas
        cur.execute("""
            SELECT d.idDieta, d.descripcion, d.horaDieta, d.idCuidador, e.tipoEspecie
            FROM dieta d
            JOIN especie e ON d.idEspecie = e.idEspecie
            WHERE d.horaDieta IS NOT NULL
              AND d.notificada = 0
              AND TIME(d.horaDieta) <= TIME(NOW())
        """)
        dietas = cur.fetchall()

        for d in dietas:
            # Crear NOTIFICACIÓN
            cur.execute("""
                INSERT INTO notificacion (idUsuario, titulo, descripcion, fecha, leida)
                VALUES (%s, %s, %s, NOW(), 0)
            """, (
                d["idCuidador"],
                "Confirmar alimentación",
                f"Dieta {d['descripcion']} de especie {d['tipoEspecie']} — ¿El animal comió? |{d['idDieta']}",
            ))

            # Marcar como ya notificada
            cur.execute("""
                UPDATE dieta SET notificada = 1 WHERE idDieta = %s
            """, (d["idDieta"],))

        conn.commit()
        cur.close()
        conn.close()
