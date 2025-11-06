import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from db import get_connection

eventos = Blueprint("eventos", __name__)

UPLOAD_FOLDER = "static/uploads"  # Carpeta para guardar las fotos


@eventos.route("/registro_cirugia", methods=["GET", "POST"])
def registro_cirugia():
    if request.method == "POST":
        id_animal = request.form.get("idAnimal")
        responsable = request.form.get("responsableCirugia")
        procedimiento = request.form.get("procedimientoCirugia")
        preparacion = request.form.get("preparacionCirugia")
        proxima = request.form.get("proximaCirugia")
        fecha = request.form.get("fechaCirugia")

        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO cirugia
            (idAnimal, responsableCirugia, procediientoCirugia, preparacionCirugia, proximaCirugia, fechaCirugia)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (id_animal, responsable, procedimiento, preparacion, proxima, fecha))
        conn.commit()
        cur.close()
        conn.close()

        flash("Cirugía registrada correctamente", "success")
        return redirect(url_for("eventos.registro_cirugia"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("cirugia.html", animales=animales)


@eventos.route("/registro_medicacion", methods=["GET", "POST"])
def registro_medicacion():
    if request.method == "POST":
        id_animal = request.form.get("id_animal")  # Asegúrate que coincida con el name del select
        nombre_med = request.form.get("nombreMed")
        dosis = request.form.get("dosisSuministradas")
        unidad = request.form.get("unidad")
        hora_aplicacion = request.form.get("horaAplicacion")
        hora_siguiente = request.form.get("horaSiguiente")
        administracion = request.form.get("administracionMed")
        reacciones = request.form.get("reaccionesMed")

        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO medicacion 
            (idAnimal, nombreMed, dosisSuministradas, horaAplicacion, horaSiguienteaplicacion, administracionMed, reaccionesMed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            id_animal, nombre_med, f"{dosis} {unidad}", hora_aplicacion, hora_siguiente, administracion, reacciones
        ))
        conn.commit()
        cur.close()
        conn.close()

        flash("Medicación registrada correctamente", "success")
        return redirect(url_for("eventos.registro_medicacion"))

    # Cargar animales para el select
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")  # 👈 nombre correcto de la tabla
    animales = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("medicacion.html", animales=animales)


@eventos.route("/registro_postoperatorio", methods=["GET", "POST"])
def registro_postoperatorio():
    if request.method == "POST":
        id_animal = request.form.get("idAnimal")
        nombre_med = request.form.get("nombreMed")
        dosis = request.form.get("dosisSuministradas")
        unidad = request.form.get("unidad")
        frecuencia = request.form.get("frecuenciaMed")
        duracion = request.form.get("duracion")
        cuidados = request.form.get("cuidadosEspecificos")
        dieta = request.form.get("dietaEspecifica")
        control = request.form.get("controlPostoperatorio")

        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO postoperatorio
            (idAnimal, nombreMed, dosisSuministrada, frecuenciaMed, duracion, cuidadosEpecificos, dietaEspecifica, controlPostoperatorio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            id_animal, nombre_med, f"{dosis} {unidad}", frecuencia, duracion, cuidados, dieta, control
        ))
        conn.commit()
        cur.close()
        conn.close()

        flash("Postoperatorio registrado correctamente", "success")
        return redirect(url_for("eventos.registro_postoperatorio"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("postoperatorio.html", animales=animales)


@eventos.route("/registro_terapia", methods=["GET", "POST"])
def registro_terapia():
    if request.method == "POST":
        id_animal = request.form.get("idAnimal")
        tipo_terapia = request.form.get("tipoTerapia")
        objetivo = request.form.get("objetivoSesion")
        dia = request.form.get("diaSesion")
        proxima = request.form.get("proximaSesion")
        duracion = request.form.get("duracionSesion")
        evaluacion = request.form.get("evaluacion")

        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO terapiafisica
            (idAnimal, tipoTerapia, objetivoSesion, diaSesion, proximaSesion, duracionSesion, evaluacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (id_animal, tipo_terapia, objetivo, dia, proxima, duracion, evaluacion))
        conn.commit()
        cur.close()
        conn.close()

        flash("Terapia física registrada correctamente", "success")
        return redirect(url_for("eventos.registro_terapia"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("terapiafisica.html", animales=animales)


@eventos.route("/registro_vacuna", methods=["GET", "POST"])
def registro_vacuna():
    if request.method == "POST":
        id_animal = request.form.get("idAnimal")
        responsable = request.form.get("responsable")
        tipo_vacuna = request.form.get("tipoVacuna")
        laboratorio = request.form.get("laboratorio")
        lote = request.form.get("lote")
        fecha_aplicacion = request.form.get("aplicacionVacuna")
        fecha_proxima = request.form.get("proximaVacuna")

        archivo = request.files.get("foto")
        if archivo and archivo.filename != "":
            filename = secure_filename(archivo.filename)
            archivo.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            filename = None

        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO vacuna
            (idAnimal, responsable, tipoVacuna, laboratorio, lote, aplicacionVacuna, proximaVacuna, vacunasAplicadas, foto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (id_animal, responsable, tipo_vacuna, laboratorio, lote, fecha_aplicacion, fecha_proxima, 1, filename))
        conn.commit()
        cur.close()
        conn.close()

        flash("Vacuna registrada correctamente", "success")
        return redirect(url_for("eventos.registro_vacuna"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("vacuna.html", animales=animales)


@eventos.route("/registro_visita", methods=["GET", "POST"])
def registro_visita():
    if request.method == "POST":
        id_animal = request.form.get("idAnimal")
        veterinario = request.form.get("veterinario")
        motivo = request.form.get("motivo")
        diagnostico = request.form.get("diagnostico")
        tratamiento = request.form.get("tratamiento")
        proxima_visita = request.form.get("fecha")
        estado = request.form.get("estado")

        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO visitas
            (idAnimal, veterinario, motivoConsulta, diagnostico, tratamiento, proximaVisita, estadoSalud)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (id_animal, veterinario, motivo, diagnostico, tratamiento, proxima_visita, estado))
        conn.commit()
        cur.close()
        conn.close()

        flash("Visita médica registrada correctamente", "success")
        return redirect(url_for("eventos.registro_visita"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("visitamedica.html", animales=animales)
