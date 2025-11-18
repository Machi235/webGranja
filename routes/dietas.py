from flask import Blueprint, render_template, request, jsonify, session
from db import get_connection
from datetime import datetime

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

            # Insertar dieta
            cur.execute("""
                INSERT INTO dieta (idEspecie, descripcion, definitivo)
                VALUES (%s, %s, %s)
            """, (idEspecie, descripcion, definitivo))
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

            # Crear notificaciones
            cur.execute("SELECT idUsuario FROM usuarios WHERE rol IN ('Admin','Cuidador') AND activo=1")
            destinatarios = cur.fetchall()
            titulo = "Nueva Dieta Registrada"
            desc_notif = f"Se registró una dieta para la especie ID: {idEspecie}"
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

        return render_template(
            "crearDieta.html",
            especies=especies,
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
        idEspecie_filtro = request.args.get("idEspecie", type=int)

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
        params = ()
        if idEspecie_filtro:
            sql += " WHERE d.idEspecie = %s"
            params = (idEspecie_filtro,)
        sql += " ORDER BY d.idDieta DESC"

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
            filtro_idEspecie=idEspecie_filtro
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
