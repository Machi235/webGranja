# LiveStock Log
_El software Livestock Log está diseñado para la gestión documental de la granja, con este es posible organizar de manera eficiente las tareas diarias, mejorar la comunicación entre el personal y procura tener un control más eficaz de la documentación de como se ha llevado hasta el momento. Vale la pena ya que con un control adecuado permitirá incrementar la eficiencia y una mejor calidad en las actividades que se realizan en la granja._

## Comenzando 🚀
_Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas._

Para poner en funcionamiento el proyecto, siga los pasos descritos a continuación:

1. Clonar el repositorio

> Descargue el código fuente desde GitHub y acceda a la carpeta del proyecto:

```
git clone https://github.com/Machi235/webGranja.git
```

```
cd webGranja
```
### Pre-requisitos 📋

Sistema operativo: Windows 10 o superior
Python: versión 3.10 o superior
Flask: versión 2.2+
Gestor de paquetes: pip
Base de datos:
MySQL/ MariaDB

Instalación de Python

> Descargue la versión más reciente de Python 3.10 o superior desde el sitio oficial.
```
https://www.python.org/downloads/
```
> Ejecute el instalador y marque la opción:
```
“Add Python to PATH”
```
> Complete la instalación siguiendo las instrucciones del asistente.

### Instalación 🔧
_Una serie de ejemplos paso a paso que te dice lo que debes ejecutar para tener un entorno de desarrollo ejecutandose_

_Crear y activar el entorno virtual_

   >Genere un entorno virtual para aislar las dependencias del proyecto y actívelo:

```
python -m venv venv
venv\Scripts\activate
```

Instalar las dependencias

   >Instale todas las librerías necesarias para el funcionamiento del aplicativo:

```
pip install -r requirements.txt
```
Ejecutar la aplicación

>Exporta las variables de la base de datos guardadad en railway

```
$env:DB_HOST = "ballast.proxy.rlwy.net"
>> $env:DB_USER = "root"
>> $env:DB_PASSWORD = "fiAqNZGlOOxQgWsWVOdPdfJWftiRiMdZ"
>> $env:DB_NAME = "railway"
>> $env:DB_PORT = "33844"
```
>Inicie el servidor ejecutando el archivo flask:
```
set FLASK_APP=app.py                   
>> set FLASK_ENV=development
>> flask run
```
### Despliegue 📦
>Desplegado con:
```
Vercel - Frontend y Backend
Railway - Base de datos MySql
```
Cada commit hecho y cada push hecho hace un nuevo deploy automático en vercel

#### Construido con 🛠️

Flask - El framework web usado,
Python - Lenguaje de programación Backend,
Html, Css y bootstrap - Frontend
>Dominio del proyecto:
```
https://web-granja.vercel.app/
```
#### Autores ✒️
_Michell Ruiz_,
_Laura Mayorga_,
_Jimmy Cano_

