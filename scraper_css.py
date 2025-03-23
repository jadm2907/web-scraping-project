import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

# URL base del sitio web
base_url = "https://www.renovare.cl/"

# Carpeta para guardar los archivos CSS
output_folder = "renovare_css"
os.makedirs(output_folder, exist_ok=True)

# Conjunto para almacenar las URLs ya visitadas
visited_urls = set()

# Función para descargar un archivo CSS
def download_css(url, filename):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        # Guardar el contenido CSS en un archivo
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"Descargado: {filename}")

    except Exception as e:
        print(f"Error al descargar {url}: {e}")

# Función para extraer CSS de una página
def extract_css(url):
    try:
        # Hacer la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()

        # Parsear el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer CSS en línea (etiquetas <style>)
        inline_css = soup.find_all('style')
        if inline_css:
            filename = os.path.join(output_folder, f"inline_css_{len(visited_urls)}.css")
            with open(filename, "w", encoding="utf-8") as file:
                for style in inline_css:
                    file.write(style.text)
            print(f"Guardado CSS en línea: {filename}")

        # Extraer CSS externo (etiquetas <link>)
        for link in soup.find_all('link', rel='stylesheet'):
            css_url = urljoin(base_url, link['href'])
            if css_url not in visited_urls:
                visited_urls.add(css_url)
                filename = os.path.join(output_folder, os.path.basename(css_url))
                download_css(css_url, filename)

        # Buscar enlaces internos y seguir rastreando
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)

            # Verificar si el enlace es del mismo dominio y no ha sido visitado
            if full_url.startswith(base_url) and full_url not in visited_urls:
                visited_urls.add(full_url)
                extract_css(full_url)  # Llamada recursiva para rastrear la nueva URL

    except Exception as e:
        print(f"Error al procesar {url}: {e}")

# Iniciar el rastreo desde la página principal
visited_urls.add(base_url)
extract_css(base_url)

print("Extracción de CSS completada.")