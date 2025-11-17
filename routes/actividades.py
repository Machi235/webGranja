from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_connection
from datetime import datetime

actividad_bp = Blueprint("actividad_bp", __name__)

@actividad_bp.route("/registro_actividad", methods=["GET", "POST"])
def registro_actividad():

    if request.method == "GET":
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Para GET: traer datos para los selects
        cur.execute(""" SELECT e.idEspecie, e.tipoEspecie, COUNT(c.idActividad) AS usadas, e.limite, NOW() - INTERVAL e.periodo DAY AS fechaLimite FROM especie AS e
                    LEFT JOIN actividades AS a ON a.idEspecie = e.idEspecie AND activo=1 LEFT JOIN cronogramaactividades AS c on c.idActividad = a.idActividad AND 
                    c.fechaCreacion >= NOW() - INTERVAL e.periodo DAY GROUP BY e.idEspecie HAVING usadas < e.limite """)
        especies = cur.fetchall()

        cur.execute("SELECT idUsuario, nombre, apellido FROM usuarios  WHERE activo = 1 AND rol= 'Guia' ORDER BY nombre;")
        usuarios = cur.fetchall()

        cur.execute("SELECT idHabitat, nombreHabitat FROM habitat WHERE activo = 1 ORDER BY nombreHabitat")
        habitats = cur.fetchall()

        cur.close()
        conn.close()

        return render_template("actividad.html", especies=especies, usuarios=usuarios, habitats=habitats)

    elif request.method == "POST":
    
        id_especies = request.form.getlist("idEspecie")
        id_usuario = request.form.get("idUsuario")
        id_habitats = request.form.getlist("idHabitat")
        tipo = request.form.get("tipo")
        horas = request.form.get("horas") or 0
        minutos = request.form.get("minutos") or 0
        fechaRealizacion = request.form.get("fechaRealizacion")
        detalles = request.form.get("detalles")
   
        duracion = f"{int(horas):02d}:{int(minutos):02d}"

        fecha = datetime.now().strftime("%Y-%m-%d")

        conn = get_connection()
        cur = conn.cursor()

        if not id_especies or not  id_usuario or not tipo or not id_habitats or not horas or not minutos or not fechaRealizacion or not detalles :
            flash("Faltan campos obligatorios", "error")
            return redirect(url_for("actividad_bp.registro_actividad"))
        else:
            cur.execute(""" 
                INSERT INTO cronogramaactividades (idUsuario, tipo, fechaCreacion, duracion, detalles, fechaRealizacion) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_usuario, tipo, fecha, duracion, detalles, fechaRealizacion ))

            id_actividad = cur.lastrowid

            mensajes = []
            for id_especie in id_especies:
                cur.callproc("limite_de_uso1",(id_especie,id_actividad))
                resultados = list(cur.stored_results())
                result=resultados[-1]
                mensaje = result.fetchone()[0]
                mensajes.append(mensaje.strip()) 
    
            for id_habitat in id_habitats:
                cur.execute("""INSERT INTO actividades (idHabitat, idActividad ) VALUES (%s, %s)""",(id_habitat, id_actividad))

        titulo = "Nueva Actividad Asignada"
        descripcion = f"Se te ha asignado una actividad de tipo '{tipo}' para la fecha {fechaRealizacion}."
        cur.execute("""
            INSERT INTO notificacion (idUsuario, titulo, rol, descripcion, fecha, leida)
            VALUES (%s, %s, 'Guia', %s, NOW(), 0)
        """, (id_usuario, titulo, descripcion))

        conn.commit()
        cur.close()
        conn.close()

        mensaje_unico = "<br>".join(mensajes)
        flash(mensaje_unico, "success")

    return render_template("actividad.html")


@actividad_bp.route("/actividades", methods=["GET"])
def ver_actividades():
    conn=get_connection()
    cur=conn.cursor(dictionary=True)

    cur.execute("""select C.idActividad, nombre, apellido, group_concat(distinct tipoEspecie separator ',') as especie, group_concat(distinct nombreHabitat separator ',') 
                as habitat, c.tipo, fechaCreacion, duracion, detalles, fechaRealizacion, limite from cronogramaactividades as c inner join actividades as a on 
                c.idActividad = a.idActividad left join usuarios as u on c.idUsuario = u.idUsuario left join especie as e on a.idEspecie =e.idEspecie left join habitat as h 
                on a.idHabitat = h.idHabitat WHERE c.estado = 1 group by a.idActividad""")
    
    actividades=cur.fetchall()

    cur.execute("SELECT limite FROM especie LIMIT 1")
    limite = cur.fetchone()['limite']   

    cur.close()
    conn.close()

    return render_template("verActividad.html", actividades=actividades, limite=limite)

@actividad_bp.route("/uso de animales", methods=["POST"])
def uso_animales():

    limite = request.form.get("limite")
    conn=get_connection()
    cur=conn.cursor()

    cur.execute(" UPDATE especie SET limite = %s", (limite,))
    conn.commit()

    conn.close()
    cur.close()

    return redirect (url_for("actividad_bp.ver_actividades"))

@actividad_bp.route("/Editar actividad/<int:idActividad>", methods=["GET"])
def editar_actividad(idActividad):
    conn=get_connection()
    cur=conn.cursor(dictionary=True)

    cur.execute("SELECT idEspecie, tipoEspecie FROM especie ORDER BY tipoEspecie")
    especies = cur.fetchall()

    cur.execute("SELECT idUsuario, nombre, apellido FROM usuarios  WHERE activo = 1 ORDER BY nombre;")
    usuarios = cur.fetchall()

    cur.execute("SELECT idHabitat, nombreHabitat FROM habitat WHERE activo = 1 ORDER BY nombreHabitat")
    habitats = cur.fetchall()

    cur.execute("""select C.idActividad,c.idUsuario, nombre, apellido, group_concat(distinct e.idEspecie separator ',') as especie_ids, group_concat(distinct tipoEspecie separator ',') as especie_nombres,  group_concat(distinct h.idHabitat separator ',') AS ids_habitats ,group_concat(distinct nombreHabitat separator ',')
                as habitat, c.tipo, fechaCreacion, duracion, detalles, fechaRealizacion from cronogramaactividades as c inner join actividades as a on 
                c.idActividad = a.idActividad left join usuarios as u on c.idUsuario = u.idUsuario left join especie as e on a.idEspecie =e.idEspecie left join habitat as h 
                on a.idHabitat = h.idHabitat  WHERE c.idActividad = %s group by a.idActividad  """, (idActividad,))
    
    actividad=cur.fetchone()

    selected_especies = [int(x.strip()) for x in actividad['especie_ids'].split(',') if x.strip()]
    selected_habitats = [int(x.strip()) for x in actividad['ids_habitats'].split(',') if x.strip()]

    conn.close()
    cur.close()

    return render_template("editarActividad.html", actividad=actividad, especies=especies, usuarios=usuarios, habitats=habitats, selected_especies=selected_especies, selected_habitats=selected_habitats)

@actividad_bp.route("Actualizar actividad/<int:idActividad>", methods=["POST"])
def actualizar_actividad(idActividad):

        # Capturar datos del formulario
    id_especies = request.form.getlist("idEspecie")
    id_usuario = request.form.get("idUsuario")
    id_habitats = request.form.getlist("idHabitat")
    tipo = request.form.get("tipo")
    duracion = request.form.get("duracion") or 0
    fechaRealizacion = request.form.get("fechaRealizacion")
    detalles = request.form.get("detalles")
        
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" UPDATE cronogramaactividades SET idUsuario = %s, tipo = %s, duracion = %s, detalles = %s, fechaRealizacion = %s WHERE idActividad=%s""", 
                (id_usuario, tipo, duracion,  detalles, fechaRealizacion, idActividad ))
    
    conn.commit()

    cur.close()
    conn.close()
    return redirect (url_for("actividad_bp.ver_actividades"))

@actividad_bp.route("/eliminar actividad/<int:idActividad>", methods=["POST"])
def eliminar_actividad(idActividad):

    conn=get_connection()
    cur=conn.cursor()

    cur.execute(""" UPDATE cronogramaactividades SET estado = 0 WHERE idActividad = %s""",(idActividad,))
    cur.execute(""" UPDATE actividades SET activo = 0 WHERE idActividad = %s""",(idActividad,))

    conn.commit()

    conn.close()
    cur.close()

    return redirect (url_for("actividad_bp.ver_actividades"))

