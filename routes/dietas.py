from flask import Blueprint, render_template, request, jsonify
from db import get_connection

dietas = Blueprint("dietas", __name__)

@dietas.route("/crear_dieta", methods=["GET", "POST"])
def crear_dieta():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        try:
            # 1. Recoger datos principales
            idAnimal = request.form.get("idAnimal")
            tipoDieta = request.form.get("tipoDieta")
            definitivo = 1 if request.form.get("definitivo") == "1" else 0

            # --- Obtener especie automáticamente del animal ---
            cur.execute("""
                SELECT especie FROM animal WHERE idAnimal = %s
            """, (idAnimal,))
            especie_data = cur.fetchone()

            if not especie_data:
                return "Error: Animal no encontrado", 404

            idEspecie = especie_data["especie"]

            # 2. Insertar en la tabla dieta
            sql_dieta = """
                INSERT INTO dieta (idAnimal, idEspecie, tipoDieta, definitivo)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(sql_dieta, (idAnimal, idEspecie, tipoDieta, definitivo))
            idDieta = cur.lastrowid

            # 3. Insertar en la tabla dietaalimento
            idAlimentos = request.form.getlist("idAlimento[]")
            cantidades = request.form.getlist("cantidadAlimento[]")
            frecuencias = request.form.getlist("frecuenciaAlimento[]")

            for i in range(len(idAlimentos)):
                if idAlimentos[i]:
                    sql_dieta_alimento = """
                        INSERT INTO dietaalimento (idDieta, idAlimento, cantidadAlimento, frecuenciaAlimento)
                        VALUES (%s, %s, %s, %s)
                    """
                    cur.execute(sql_dieta_alimento, (
                        idDieta,
                        idAlimentos[i],
                        cantidades[i],
                        frecuencias[i]
                    ))

            conn.commit()

            return "OK", 200  # ✅ Sin JSON, solo un mensaje simple

        except Exception as e:
            conn.rollback()
            print("Error al crear dieta:", str(e))
            return "Error interno del servidor", 500

        finally:
            cur.close()
            conn.close()

    # GET: Mostrar formulario
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()

    cur.execute("SELECT idAlimento, origen FROM alimento ORDER BY origen")
    alimentos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("crearDieta.html", animales=animales, alimentos=alimentos)

ALIMENTOS_POR_ESPECIE = {
    "Gallina": ["Maíz", "Sorgo", "Salvado de trigo", "Harina de pescado", "Cáscaras de huevo"],
    "Caballo": ["Pasto fresco", "Avena", "Zanahoria", "Heno", "Sal mineralizada"],
    "Vaca": ["Pasto", "Maíz", "Heno", "Sal mineralizada", "Sorgo"],
    "Toro": ["Pasto", "Maíz", "Heno", "Sal mineralizada", "Sorgo"],
    "Cerdo": ["Maíz", "Soya", "Trigo", "Salvado de trigo", "Restos de vegetales"],
    "Perro": ["Croquetas", "Pollo cocido", "Hígado", "Arroz", "Verduras"],
    "Gato": ["Croquetas", "Pescado", "Pollo cocido", "Hígado", "Leche"]
}

@dietas.route("/alimentos_por_animal/<int:idAnimal>", methods=["GET"])
def alimentos_por_animal(idAnimal):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # 1. Obtener especie del animal
    cur.execute("""
        SELECT e.tipoEspecie 
        FROM animal a
        INNER JOIN especie e ON a.especie = e.idEspecie
        WHERE a.idAnimal = %s
    """, (idAnimal,))
    resultado = cur.fetchone()
    
    if not resultado:
        cur.close()
        conn.close()
        return jsonify([])  # No se encontró el animal

    especie = resultado["tipoEspecie"]

    # 2. Buscar alimentos correspondientes
    alimentos_permitidos = ALIMENTOS_POR_ESPECIE.get(especie, [])

    # 3. Traer alimentos desde la tabla `alimento`
    formato = ",".join(["%s"] * len(alimentos_permitidos))
    sql = f"SELECT idAlimento, origen FROM alimento WHERE origen IN ({formato}) ORDER BY origen"
    cur.execute(sql, tuple(alimentos_permitidos))
    alimentos = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(alimentos)

@dietas.route("/ver_dietas", methods=["GET"])
def ver_dietas():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    try:
        # --- Filtros opcionales ---
        idAnimal = request.args.get("idAnimal")
        idEspecie = request.args.get("idEspecie")

        sql = """
            SELECT
                d.idDieta, d.tipoDieta, d.definitivo,
                a.idAnimal, a.nombre AS nombreAnimal,
                e.idEspecie, e.tipoEspecie,
                da.idAlimento, al.origen AS nombreAlimento,
                da.cantidadAlimento, da.frecuenciaAlimento
            FROM dieta d
            JOIN animal a ON d.idAnimal = a.idAnimal
            JOIN especie e ON d.idEspecie = e.idEspecie
            LEFT JOIN dietaalimento da ON d.idDieta = da.idDieta
            LEFT JOIN alimento al ON da.idAlimento = al.idAlimento
            WHERE 1=1
        """

        params = []
        if idAnimal:
            sql += " AND a.idAnimal = %s"
            params.append(idAnimal)
        if idEspecie:
            sql += " AND e.idEspecie = %s"
            params.append(idEspecie)

        sql += " ORDER BY d.idDieta DESC"

        cur.execute(sql, params)
        rows = cur.fetchall()

        # --- Agrupar alimentos por dieta ---
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

        # Datos para filtros
        cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
        animales = cur.fetchall()

        cur.execute("SELECT idEspecie, tipoEspecie FROM especie ORDER BY tipoEspecie")
        especies = cur.fetchall()

        return render_template("verDietas.html",
                               dietas=list(dietas_dict.values()),
                               animales=animales,
                               especies=especies)

    except Exception as e:
        print("ERROR DETALLADO ver_dietas:", repr(e))
        return jsonify({"error": "Ocurrió un error al cargar las dietas"}), 500
    finally:
        cur.close()
        conn.close()
