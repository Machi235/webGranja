from flask import Blueprint, render_template, request, flash, url_for, redirect
from db import get_connection

boleto = Blueprint("ventaBoleto",__name__)

@boleto.route("/Boletos-vendidos", methods=["GET"])
def ver_boletas():

    conn=get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(" SELECT nombre, correo, telefono, tipo, metodopago, cantidad FROM boletos ")
    boletos=cur.fetchall()

    cur.close()
    conn.close()

    return render_template("boletas.html", boletos=boletos)

@boleto.route("/venta-de-boletos", methods=["GET","POST"])
def boleta():
    nombre1 = request.form.get("nombre")
    correo2 = request.form.get("correo")
    numero = request.form.get("numero")
    tipo = request.form.get("tipo")
    pago = request.form.get("pago")
    cantidad = request.form.get("cantidad")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO boletos (nombre, correo, telefono, tipo, metodopago, cantidad) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre1, correo2, numero, tipo, pago, cantidad))
    
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("ventaBoleto.ver_boletas"))