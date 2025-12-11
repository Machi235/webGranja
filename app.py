from flask import Flask
from routes.auth import auth
from routes.animales import animales
from routes.main import main
from routes.habitat import habitat_bp
from routes.turnos import turnos_bp
from routes.eventosClinicos import eventos
from routes.actividades import actividad_bp
from routes.asignacionhabitad import asignacion
from routes.buscarHabitat import bp as buscarHabitat_bp
from routes.dietas import dietas, check_dietas_background
from flask_mail import Mail
from routes.eventos import eventos_general
from routes.ventaBoleta import boleto
from routes.notificacion import notificaciones_bp
from routes.reporte import reporte
from routes.tareas import tareas
from routes.alimento import alimento_bp
from routes.especies import especies_bp
from routes.access import access_bp
from routes.recordatorio import revisar_recordatorios

# ---------------------------------------------
#   CONFIGURACIÓN BASE DE LA APLICACIÓN
# ---------------------------------------------

app = Flask(__name__)
app.secret_key = "super_clave_ultra_secreta_123"
app.config["UPLOAD_FOLDER"] = "static/uploads/usuarios"

# ---------------------------------------------
#   CONFIGURACIÓN MAIL
# ---------------------------------------------

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'santyenglish333@gmail.com'
app.config['MAIL_PASSWORD'] = 'wrakngwivfpvffmb'  # contraseña de aplicación Google
app.config['MAIL_DEFAULT_SENDER'] = ('Granja Machis', 'santyenglish333@gmail.com')

mail = Mail(app)

# ---------------------------------------------
#   BLUEPRINTS
# ---------------------------------------------

app.register_blueprint(auth)
app.register_blueprint(animales)
app.register_blueprint(eventos)
app.register_blueprint(main)
app.register_blueprint(asignacion)
app.register_blueprint(habitat_bp, url_prefix="/habitat")
app.register_blueprint(turnos_bp, url_prefix="/turnos")
app.register_blueprint(actividad_bp, url_prefix="/actividad")
app.register_blueprint(buscarHabitat_bp)
app.register_blueprint(dietas, url_prefix="/dietas")
app.register_blueprint(eventos_general)
app.register_blueprint(alimento_bp)
app.register_blueprint(boleto)
app.register_blueprint(notificaciones_bp)
app.register_blueprint(reporte)
app.register_blueprint(tareas)
app.register_blueprint(especies_bp)
app.register_blueprint(access_bp)

# ---------------------------------------------
#   RUTAS PARA CRONJOBS (Vercel)
# ---------------------------------------------

@app.route("/cron/revisar_recordatorios")
def cron_revisar_recordatorios():
    """Ruta llamada por Vercel Cron para ejecutar los recordatorios."""
    revisar_recordatorios()
    return "Recordatorios ejecutados"

@app.route("/cron/check_dietas")
def cron_check_dietas():
    """Ruta llamada por Vercel Cron para revisar dietas."""
    check_dietas_background(app)
    return "Dietas revisadas"

# ---------------------------------------------
#   IMPORTANTE: Vercel NO usa app.run()
# ---------------------------------------------
# NO INCLUIR app.run(debug=True)

# El archivo termina aquí.
