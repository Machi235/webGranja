from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection
from datetime import datetime

actividad_bp = Blueprint("actividad_bp", __name__)

@actividad_bp.route("/registro_actividad", methods=["GET", "POST"])
def registro_actividad():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # Para GET: traer datos para los selects
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()

    cur.execute("SELECT idUsuario, nombre FROM usuarios ORDER BY nombre")
    usuarios = cur.fetchall()

    cur.execute("SELECT idHabitat, nombreHabitat FROM habitat ORDER BY nombreHabitat")
    habitats = cur.fetchall()

    if request.method == "POST":
        # Capturar datos del formulario
        id_animal = request.form.get("idAnimal")
        id_usuario = request.form.get("idUsuario")
        habitat = request.form.get("habitat")
        tipo = request.form.get("tipo")
        horas = request.form.get("horas") or 0
        minutos = request.form.get("minutos") or 0
        detalles = request.form.get("detalles")
        
        # Combinar horas y minutos en formato HH:MM
        duracion = f"{int(horas):02d}:{int(minutos):02d}"

        # Fecha actual para la actividad
        fecha = datetime.now().strftime("%Y-%m-%d")

        # Insertar en la base de datos
        sql = """
            INSERT INTO actividades
            (idAnimal, idUsuario, tipo, habitat, fecha, hora, detalles)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (id_animal, id_usuario, tipo, habitat, fecha, duracion, detalles))
        conn.commit()
        flash("✅ Actividad registrada correctamente")
        return redirect(url_for("actividad_bp.registro_actividad"))

    cur.close()
    conn.close()
    return render_template(
        "actividad.html",
        animales=animales,
        usuarios=usuarios,
        habitats=habitats
    )
