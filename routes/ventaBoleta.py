from flask import Blueprint, render_template, request, redirect, url_for
from flask_mail import Message
from db import get_connection

boleto = Blueprint("ventaBoleto", __name__)

@boleto.route("/Boletos-vendidos", methods=["GET"])
def ver_boletas():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT nombre, correo, telefono, tipo, metodopago, cantidad FROM boletos")
    boletos = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("boletas.html", boletos=boletos)

@boleto.route("/venta-de-boletos", methods=["GET","POST"])
def boleta():
    from servidor import mail  # ⚡ Importación dentro de la función para evitar circularidad

    if request.method == "POST":
        nombre1 = request.form.get("nombre")
        correo2 = request.form.get("correo")
        numero = request.form.get("numero")
        tipo = request.form.get("tipo")
        pago = request.form.get("pago")
        cantidad = request.form.get("cantidad")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO boletos (nombre, correo, telefono, tipo, metodopago, cantidad) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre1, correo2, numero, tipo, pago, cantidad)
        )
        conn.commit()
        cur.close()
        conn.close()

        # Enviar correo de confirmación
        try:
            msg = Message(
                subject="Confirmación de tu boleto",
                sender="TU_CORREO@gmail.com",
                recipients=[correo2],
                body=f"""
Hola {nombre1},

Gracias por tu compra. Aquí están los detalles de tu boleto:

- Tipo de boleto: {tipo}
- Cantidad: {cantidad}
- Método de pago: {pago}
- Número de contacto: {numero}

¡Disfruta del evento!

Saludos,
El equipo del evento
                """
            )
            mail.send(msg)
        except Exception as e:
            print("Error al enviar el correo:", e)

        return redirect(url_for("ventaBoleto.ver_boletas"))

    return render_template("ventaBoleta.html")
