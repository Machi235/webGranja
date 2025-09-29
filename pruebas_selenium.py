from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import os

# ===== CONFIGURACIONES =====
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
BIENVENIDA_URL = f"{BASE_URL}/bienvenida"

# Credenciales de prueba
USUARIO = "vane"           # Ajusta esto según tu base de datos
PASSWORD = "1234"          # Ajusta esto según tu base de datos

# Carpeta para guardar capturas
CAPTURAS_DIR = "capturas_bienvenida"
os.makedirs(CAPTURAS_DIR, exist_ok=True)

# ===== CONFIGURACIÓN DEL DRIVER =====
def setup_driver():
    """Configura el driver de Chrome"""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    return driver

# ===== LOGIN AUTOMÁTICO =====
def login(driver):
    """Realiza login en la aplicación"""
    print(f"🌐 Navegando a {LOGIN_URL}")
    driver.get(LOGIN_URL)

    try:
        # Esperar que el campo usuario aparezca
        usuario_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "usuario"))
        )
        usuario_input.send_keys(USUARIO)
        print("✅ Usuario ingresado")

        # Contraseña
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(PASSWORD)
        print("✅ Contraseña ingresada")

        # Captura antes de enviar el formulario
        driver.save_screenshot(os.path.join(CAPTURAS_DIR, "antes_login.png"))

        # Botón ingresar
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        print("🖱️ Botón de login clickeado")

        # Esperar redirección a bienvenida
        WebDriverWait(driver, 10).until(
            EC.url_contains("/bienvenida")
        )
        print("🎉 Login exitoso, redirigido a /bienvenida")

        driver.save_screenshot(os.path.join(CAPTURAS_DIR, "despues_login.png"))

    except TimeoutException:
        print("❌ No se pudo realizar el login, revisa credenciales o conexión")
        driver.save_screenshot(os.path.join(CAPTURAS_DIR, "error_login.png"))
        raise

# ===== PRUEBA DE BIENVENIDA =====
def test_home_bienvenida():
    print("🚀 Iniciando prueba de /bienvenida")
    driver = setup_driver()

    try:
        # 1. Primero hacer login
        login(driver)

        # 2. Asegurarnos que estamos en /bienvenida
        driver.get(BIENVENIDA_URL)
        print(f"🌐 Verificando página: {BIENVENIDA_URL}")

        driver.implicitly_wait(5)

        # Screenshot inicial
        driver.save_screenshot(os.path.join(CAPTURAS_DIR, "bienvenida_inicial.png"))

        # 3. Elementos clave a verificar
        elementos_clave = [
            (By.TAG_NAME, "nav", "Barra de navegación"),
            (By.CLASS_NAME, "navbar-toggler", "Botón menú hamburguesa"),
            (By.ID, "notiPanel", "Panel de notificaciones"),
            (By.ID, "carouselExampleCaptions", "Carrusel principal"),
            (By.CLASS_NAME, "card", "Cards principales"),
            (By.TAG_NAME, "footer", "Footer de la página")
        ]

        print("\n⏳ Verificando elementos en la página...")
        encontrados = 0

        for tipo, valor, descripcion in elementos_clave:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((tipo, valor))
                )
                print(f"   ✅ {descripcion} encontrado -> {tipo}='{valor}'")
                encontrados += 1
            except TimeoutException:
                print(f"   ❌ {descripcion} NO encontrado -> {tipo}='{valor}'")

        driver.save_screenshot(os.path.join(CAPTURAS_DIR, "bienvenida_elementos.png"))

        # 4. Interacción con el menú
        print("\n🖱️ Probando menú hamburguesa...")
        try:
            boton_menu = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "navbar-toggler"))
            )
            boton_menu.click()
            print("   ✅ Menú abierto correctamente")
            time.sleep(1)

            driver.save_screenshot(os.path.join(CAPTURAS_DIR, "menu_abierto.png"))

            # Cerrar menú
            driver.find_element(By.CLASS_NAME, "btn-close").click()
            print("   ✅ Menú cerrado correctamente")
            time.sleep(1)

        except TimeoutException:
            print("   ❌ No se pudo interactuar con el menú hamburguesa")

        # 5. Probar panel de notificaciones
        print("\n🔔 Probando panel de notificaciones...")
        try:
            campana = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "noti-icon"))
            )
            campana.click()
            print("   ✅ Panel de notificaciones abierto")

            driver.save_screenshot(os.path.join(CAPTURAS_DIR, "notificaciones_abiertas.png"))

            # Cerrar panel con botón ✖
            close_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✖')]"))
            )
            close_btn.click()
            print("   ✅ Panel de notificaciones cerrado")
        except TimeoutException:
            print("   ❌ No se pudo abrir o cerrar el panel de notificaciones")

        # 6. Verificar que haya 3 cards
        print("\n📦 Verificando cards principales...")
        try:
            cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "card"))
            )
            if len(cards) >= 3:
                print(f"   ✅ Se encontraron {len(cards)} cards en la página")
            else:
                print(f"   ⚠️ Solo se encontraron {len(cards)} cards, deberían ser al menos 3")
        except TimeoutException:
            print("   ❌ No se encontraron las cards")

        driver.save_screenshot(os.path.join(CAPTURAS_DIR, "cards.png"))

        # 7. Carrusel
        print("\n🎡 Probando carrusel...")
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "carousel-control-next"))
            )
            next_button.click()
            print("   ✅ Carrusel avanzó a la siguiente imagen")

            prev_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "carousel-control-prev"))
            )
            prev_button.click()
            print("   ✅ Carrusel retrocedió a la imagen anterior")

            driver.save_screenshot(os.path.join(CAPTURAS_DIR, "carrusel.png"))

        except TimeoutException:
            print("   ❌ No se pudo interactuar con el carrusel")

        print("\n===== RESULTADOS =====")
        if encontrados == len(elementos_clave):
            print(f"🎉 Todos los {encontrados} elementos clave fueron encontrados correctamente")
        else:
            print(f"⚠️ Solo se encontraron {encontrados} de {len(elementos_clave)} elementos clave")

    except Exception as e:
        print(f"💥 Error durante la prueba: {e}")
        driver.save_screenshot(os.path.join(CAPTURAS_DIR, "error.png"))
    finally:
        driver.quit()
        print("🚪 Navegador cerrado")

# ===== EJECUTAR =====
if __name__ == "__main__":
    test_home_bienvenida()
    print("\n🏁 Prueba finalizada. Revisa la carpeta 'capturas_bienvenida'.")

