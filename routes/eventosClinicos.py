import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from db import get_connection

eventos = Blueprint("eventos", __name__)

UPLOAD_FOLDER = "static/uploads"

# --------- ENVIAR NOTIFICACIONES A ADMIN Y CUIDADORES ---------
def enviar_notificacion(titulo, descripcion):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT idUsuario FROM usuarios WHERE rol IN ('Admin', 'Cuidador') AND activo = 1")
    destinatarios = cur.fetchall()

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for d in destinatarios:
        cur.execute("""
            INSERT INTO notificacion (idUsuario, titulo, descripcion, fecha, leida)
            VALUES (%s, %s, %s, %s, 0)
        """, (d['idUsuario'], titulo, descripcion, fecha_actual))

    conn.commit()
    cur.close()
    conn.close()

# --------- GUARDAR RECORDATORIO ---------
def guardar_recordatorio(id_animal, evento, fecha_proxima, mensaje):
    if fecha_proxima:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO recordatorios (idAnimal, evento, fecha_recordatorio, mensaje, enviado)
            VALUES (%s, %s, %s, %s, 0)
        """, (id_animal, evento, fecha_proxima, mensaje))
        conn.commit()
        cur.close()
        conn.close()

# ----------------------------------------------------------------
# CIRUGÍA
# ----------------------------------------------------------------
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

        enviar_notificacion("Nueva cirugía registrada",
            f"Animal {id_animal} tuvo cirugía. Próxima revisión: {proxima or 'No indicada'}.")

        guardar_recordatorio(id_animal, "Cirugía", proxima,
            f"Control post-quirúrgico del animal {id_animal}.")

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

# ----------------------------------------------------------------
# MEDICACIÓN
# ----------------------------------------------------------------
@eventos.route("/registro_medicacion", methods=["GET", "POST"])
def registro_medicacion():
    if request.method == "POST":
        id_animal = request.form.get("id_animal")
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
            (idAnimal, nombreMed, dosisSuministradas, horaAplicacion, horaSiguienteAplicacion, administracionMed, reaccionesMed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (id_animal, nombre_med, f"{dosis} {unidad}", hora_aplicacion, hora_siguiente, administracion, reacciones))
        conn.commit()

        enviar_notificacion("Medicación aplicada",
            f"Se aplicó '{nombre_med}' al animal {id_animal}. Próxima dosis: {hora_siguiente}.")

        guardar_recordatorio(id_animal, "Medicación", hora_siguiente,
            f"Re-aplicar medicación {nombre_med} al animal {id_animal}.")

        cur.close()
        conn.close()

        flash("Medicación registrada correctamente", "success")
        return redirect(url_for("eventos.registro_medicacion"))

    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT idAnimal, nombre FROM animal ORDER BY nombre")
    animales = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("medicacion.html", animales=animales)

# ----------------------------------------------------------------
# POSTOPERATORIO
# ----------------------------------------------------------------
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
        cur.execute(sql, (id_animal, nombre_med, f"{dosis} {unidad}", frecuencia, duracion, cuidados, dieta, control))
        conn.commit()

        enviar_notificacion("Postoperatorio registrado",
            f"Animal {id_animal} está en postoperatorio. Control: {control}.")

        guardar_recordatorio(id_animal, "Postoperatorio", control,
            f"Revisar evolución de postoperatorio del animal {id_animal}.")

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

# ----------------------------------------------------------------
# TERAPIA
# ----------------------------------------------------------------
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

        enviar_notificacion("Terapia registrada",
            f"Animal {id_animal} tuvo terapia. Próxima sesión: {proxima}")

        guardar_recordatorio(id_animal, "Terapia física", proxima,
            f"Hoy se debe realizar la terapia física al animal {id_animal}.")

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

# ----------------------------------------------------------------
# VACUNA
# ----------------------------------------------------------------
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
        filename = secure_filename(archivo.filename) if archivo and archivo.filename else None
        if filename:
            archivo.save(os.path.join(UPLOAD_FOLDER, filename))

        conn = get_connection()
        cur = conn.cursor()
        sql = """
            INSERT INTO vacuna
            (idAnimal, responsable, tipoVacuna, laboratorio, lote, aplicacionVacuna, proximaVacuna, vacunasAplicadas, foto)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (id_animal, responsable, tipo_vacuna, laboratorio, lote, fecha_aplicacion, fecha_proxima, 1, filename))
        conn.commit()

        enviar_notificacion("Vacuna registrada",
            f"Se aplicó vacuna {tipo_vacuna} a {id_animal}. Próxima dosis: {fecha_proxima}")

        guardar_recordatorio(id_animal, "Vacuna", fecha_proxima,
            f"Hoy toca vacunar nuevamente al animal {id_animal} con {tipo_vacuna}.")

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

# ----------------------------------------------------------------
# VISITA MEDICA
# ----------------------------------------------------------------
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

        enviar_notificacion("Visita médica registrada",
            f"Animal {id_animal} fue atendido. Próxima visita: {proxima_visita}")

        guardar_recordatorio(id_animal, "Visita médica", proxima_visita,
            f"Hoy corresponde revisar al animal {id_animal} según visita médica anterior.")

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


@eventos.route('/eventosclinicos')
def evento():
    return render_template('eventos.html')
