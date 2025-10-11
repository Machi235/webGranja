from flask import Flask
from routes.auth import auth
from routes.animales import animales
from routes.main import main
from routes.notificacion import notificaciones_bp
from routes.habitat import habitat_bp
from routes.turnos import turnos_bp
from routes.eventosClinicos import eventos
from routes.actividades import actividad_bp
from routes.asignacionhabitad import asignacion
from routes.reporte import reporte
from routes.buscarHabitat import bp as buscarHabitat_bp


app = Flask(__name__)
app.secret_key = "super_clave_ultra_secreta_123"  

# Registrar blueprints
app.register_blueprint(auth)
app.register_blueprint(animales)
app.register_blueprint(eventos)
app.register_blueprint(main)
app.register_blueprint(reporte)
app.register_blueprint(asignacion)
app.register_blueprint(notificaciones_bp, url_prefix="/notificaciones")
app.register_blueprint(habitat_bp, url_prefix="/habitat")
app.register_blueprint(turnos_bp, url_prefix="/turnos")
app.register_blueprint(actividad_bp, url_prefix="/actividad")
app.register_blueprint(buscarHabitat_bp)


if __name__ == "__main__":
    app.run(debug=True)
