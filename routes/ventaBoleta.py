from flask import Blueprint, make_response, render_template, request, redirect, url_for
from flask_mail import Message
from db import get_connection
from db import get_connection  # tu función de conexión
from io import BytesIO #Modulo de entradas y salidas
from reportlab.lib.pagesizes import letter #tamaño de papel
from reportlab.lib.styles import getSampleStyleSheet #Estilos de texto
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer #Contenido de pdf
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

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

@boleto.route("/pdf_boletos")
def generar_pdf():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT nombre, correo, telefono, tipo, metodopago, cantidad FROM boletos")
    boletos = cur.fetchall()

    buffer = BytesIO() #Crea un espacio temporal en memoria
    pdf = SimpleDocTemplate(buffer, pagesize=letter) #Se crea el documento pdf
    elements = [] #Lista vacia donde se pone el contenido
    styles = getSampleStyleSheet() #conjunto de estilos 

    elements.append(Paragraph(f"<b>Venta de boletos</b>", styles["Title"])) #Agrgar un parrafro al pdf

    datos = [["Nombre", "Correo", "Telefono", "Tipo", "Cantidad", "Metodopago"]]

    for fila in boletos:
        datos.append([
            fila["nombre"],
            fila["correo"],
            fila["telefono"],
            fila["tipo"],
            fila["cantidad"],
            fila["metodopago"]
        ])
    
    tabla = Table(datos, colWidths=[100,150,100,100,60,80])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),

        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("BACKGROUND", (0,1), (-1,-1), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(Spacer(1, 20)) #Pie de pagina
    elements.append(tabla)


    pdf.build(elements) #Crea el pdf con todos elementos en el mismo orden  

    response = make_response(buffer.getvalue()) # sE crea una respuesta http con los bytes obtenidos en el buffer    
    response.headers["Content-Type"] = "application/pdf" #Dice que el contenido es un pdf
    response.headers["Content-Disposition"] = "inline; filename=animal.pdf" #Lo abre directamente
    return response 