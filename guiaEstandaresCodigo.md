# Guía de Estándares de Código – Proyecto Flask/Python

## 1. Reglas de nombres
- Variables y funciones: `snake_case` (ej: `user_name`, `get_data()`).
- Clases: `PascalCase` (ej: `UserModel`, `AnimalRegistro`).
- Constantes: `MAYUSCULAS_CON_GUIONES` (ej: `MAX_USERS`, `API_KEY`).
- Archivos y módulos: `snake_case` (ej: `models.py`, `user_service.py`).

## 2. Comentarios y documentación
- Usar comentarios cortos y claros en español o inglés.
- Documentar funciones y clases con **docstrings**:

```python
def get_user(id: int) -> dict:
    """
    Obtiene la información de un usuario dado su ID.
    Args:
        id (int): ID del usuario
    Returns:
        dict: Datos del usuario
    """

---

## 2. Instalar linters y formateadores

En tu proyecto Flask (dentro del **entorno virtual**):

```bash
pip install black flake8
