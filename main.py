import time
import subprocess
import threading
import sys
from selenium import webdriver

# Função para iniciar o servidor Dash
def start_dash_app():
    subprocess.Popen([sys.executable, 'dash_app.py'])

# Função para abrir o navegador
def start_browser():
    driver = webdriver.Chrome()
    time.sleep(5)  # Espera o servidor iniciar
    driver.get('http://127.0.0.1:8080/')

# Função principal
if __name__ == '__main__':
    threading.Thread(target=start_dash_app, daemon=True).start()
    start_browser()
    while True:
        time.sleep(60) 