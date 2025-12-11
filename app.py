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
from routes.dietas import dietas
from flask_mail import Mail
from routes.eventos import eventos_general
from routes.ventaBoleta import boleto
from routes.notificacion import notificaciones_bp
from routes.reporte import reporte
from routes.tareas import tareas
from routes.alimento import alimento_bp
from routes.especies import especies_bp
from routes.access import access_bp
from apscheduler.schedulers.background import BackgroundScheduler
from routes.dietas import check_dietas_background
from routes.recordatorio import revisar_recordatorios

def iniciar_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: check_dietas_background(app),
                      trigger="interval", seconds=60)  # Cada 1 min
    scheduler.start()

def iniciar_scheduler(app):
    scheduler = BackgroundScheduler()
    
    scheduler.add_job(revisar_recordatorios, 'cron', hour=6, minute=0)

    # O para pruebas: cada 1 minuto
    # scheduler.add_job(revisar_recordatorios, 'interval', minutes=1)

    scheduler.start()


app = Flask(__name__)
app.secret_key = "super_clave_ultra_secreta_123"  
app.config["UPLOAD_FOLDER"] = "static/uploads/usuarios"

iniciar_scheduler(app)
# Registrar blueprints
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



app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'santyenglish333@gmail.com'  # <-- tu Gmail
app.config['MAIL_PASSWORD'] = 'wrakngwivfpvffmb'   # <-- usa una "contraseña de aplicación" de Google
app.config['MAIL_DEFAULT_SENDER'] = ('Granja Machis', 'santyenglish333@gmail.com')

mail = Mail(app)



if __name__ == "__main__":
    app.run(debug=True)
