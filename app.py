from flask import Flask, jsonify
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
from datetime import datetime

# ---------------------------------------------
#   CONFIGURACIÓN BASE DE LA APLICACIÓN
# ---------------------------------------------

app = Flask(__name__)
app.secret_key = "super_clave_ultra_secreta_123"
app.config["UPLOAD_FOLDER"] = "static/uploads/usuarios"

# ---------------------------------------------
#   CONFIGURACIÓN DE EMAIL
# ---------------------------------------------

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'santyenglish333@gmail.com'
app.config['MAIL_PASSWORD'] = 'wrakngwivfpvffmb'  # contraseña de aplicación
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
#   ENDPOINTS PARA CRON EXTERNOS (cron-job.org)
# ---------------------------------------------

@app.route("/cron/revisar_recordatorios", methods=["GET"])
def cron_revisar_recordatorios():
    """Ejecuta la función revisar_recordatorios vía un cron externo."""
    try:
        revisar_recordatorios()
        return jsonify({
            "status": "ok",
            "action": "revisar_recordatorios",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/cron/check_dietas", methods=["GET"])
def cron_check_dietas():
    """Ejecuta revisión de dietas desde cron externo."""
    try:
        check_dietas_background(app)
        return jsonify({
            "status": "ok",
            "action": "check_dietas",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ---------------------------------------------
#   IMPORTANTE PARA VERCEL
# ---------------------------------------------
# No incluir app.run() — Vercel usa un servidor interno.
