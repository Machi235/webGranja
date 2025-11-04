from flask import Blueprint, render_template, request, jsonify
from db import get_connection

dietas = Blueprint("dietas", __name__)

@dietas.route("/crear_dieta", methods=["GET", "POST"])
def crear_dieta():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        try:
            # Datos principales
            idAnimal = request.form.get("idAnimal")
            tipoDieta = request.form.get("tipoDieta")
            definitivo = 1 if request.form.get("definitivo") else 0

            # Obtener especie
            cur.execute("SELECT especie FROM animal WHERE idAnimal = %s", (idAnimal,))
            especie_data = cur.fetchone()
            if not especie_data:
                return jsonify({"error": "Animal no encontrado"}), 404
            idEspecie = especie_data["especie"]

            # Insertar dieta
            cur.execute("""
                INSERT INTO dieta (idAnimal, idEspecie, tipoDieta, definitivo)
                VALUES (%s, %s, %s, %s)
            """, (idAnimal, idEspecie, tipoDieta, definitivo))
            idDieta = cur.lastrowid

            # Insertar alimentos evitando duplicados
            idAlimentos = request.form.getlist("idAlimento[]")
            cantidades = request.form.getlist("cantidadAlimento[]")
            frecuencias = request.form.getlist("frecuenciaAlimento[]")

            alimentos_insertados = set()
            for i in range(len(idAlimentos)):
                idAlimento = idAlimentos[i]
                if idAlimento and idAlimento not in alimentos_insertados:
                    cur.execute("""
                        INSERT INTO dietaalimento (idDieta, idAlimento, cantidadAlimento, frecuenciaAlimento)
                        VALUES (%s, %s, %s, %s)
                    """, (idDieta, idAlimento, cantidades[i], frecuencias[i]))
                    alimentos_insertados.add(idAlimento)

            conn.commit()
            return jsonify({"success": True}), 200

        except Exception as e:
            conn.rollback()
            print("ERROR DETALLADO:", str(e))
            return jsonify({"error": str(e)}), 500

        finally:
            cur.close()
            conn.close()

    # GET - mostrar formulario
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()

    cur.execute("SELECT idAlimento, Origen FROM alimento ORDER BY Origen")
    alimentos = cur.fetchall()

    # Notificaciones y rol para los navs
    notificaciones_no_leidas = 0
    notificaciones = []
    from flask import session
    if 'idUsuario' in session:
        cur.execute("SELECT * FROM notificacion WHERE idUsuario = %s", (session['idUsuario'],))
        notificaciones = cur.fetchall()
        notificaciones_no_leidas = sum(1 for n in notificaciones if not n.get('leida'))

    cur.close()
    conn.close()

    return render_template(
        "crearDieta.html",
        animales=animales,
        alimentos=alimentos,
        rol=session.get("rol"),
        notificaciones_no_leidas=notificaciones_no_leidas,
        notificaciones=notificaciones
    )



@dietas.route("/alimentos_por_animal/<int:idAnimal>", methods=["GET"])
def alimentos_por_animal(idAnimal):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT especie FROM animal WHERE idAnimal = %s", (idAnimal,))
        res = cur.fetchone()
        if not res:
            return jsonify([])
        idEspecie = res["especie"]

        cur.execute("SELECT idAlimento, Origen FROM alimento WHERE idEspecie = %s ORDER BY Origen", (idEspecie,))
        alimentos = cur.fetchall()
        return jsonify(alimentos)
    except Exception as e:
        print("Error alimentos_por_animal:", e)
        return jsonify([])
    finally:
        cur.close()
        conn.close()


@dietas.route("/ver_dietas", methods=["GET"])
def ver_dietas():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT
                d.idDieta, d.tipoDieta, d.definitivo,
                a.idAnimal, a.nombre AS nombreAnimal,
                e.idEspecie, e.tipoEspecie,
                da.idAlimento, al.Origen AS nombreAlimento,
                da.cantidadAlimento, da.frecuenciaAlimento
            FROM dieta d
            JOIN animal a ON d.idAnimal = a.idAnimal
            JOIN especie e ON d.idEspecie = e.idEspecie
            LEFT JOIN dietaalimento da ON d.idDieta = da.idDieta
            LEFT JOIN alimento al ON da.idAlimento = al.idAlimento
            ORDER BY d.idDieta DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()

        dietas_dict = {}
        for row in rows:
            idDieta = row["idDieta"]
            if idDieta not in dietas_dict:
                dietas_dict[idDieta] = {
                    "idDieta": idDieta,
                    "tipoDieta": row["tipoDieta"],
                    "definitivo": row["definitivo"],
                    "idAnimal": row["idAnimal"],
                    "nombreAnimal": row["nombreAnimal"],
                    "idEspecie": row["idEspecie"],
                    "tipoEspecie": row["tipoEspecie"],
                    "alimentos": []
                }
            if row["idAlimento"]:
                dietas_dict[idDieta]["alimentos"].append({
                    "idAlimento": row["idAlimento"],
                    "nombreAlimento": row["nombreAlimento"],
                    "cantidadAlimento": row["cantidadAlimento"],
                    "frecuenciaAlimento": row["frecuenciaAlimento"]
                })

        return render_template("verDietas.html", dietas=list(dietas_dict.values()))
    except Exception as e:
        print("ERROR ver_dietas:", e)
        return jsonify({"error": "Ocurrió un error al cargar las dietas"}), 500
    finally:
        cur.close()
        conn.close()
