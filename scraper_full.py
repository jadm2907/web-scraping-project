import os
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import requests

# Configuración
base_url = "https://dnschecker.org/"
output_folder = "dnschecker_scrape"
os.makedirs(output_folder, exist_ok=True)

# Archivo para guardar metadatos
metadata_file = os.path.join(output_folder, "metadata.json")
metadata = {}

# Límite de intentos para una URL
MAX_ATTEMPTS = 5

# Límite de profundidad de rastreo
MAX_DEPTH = 3

# Verificar robots.txt
def check_robots_txt():
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        response = requests.get(robots_url)
        if response.status_code == 200:
            print("robots.txt encontrado. Respetando reglas...")
            # Aquí puedes agregar lógica para respetar las reglas de robots.txt
        else:
            print("No se encontró robots.txt. Continuando...")
    except Exception as e:
        print(f"Error al verificar robots.txt: {e}")

# Función para guardar archivos (usando ThreadPoolExecutor)
def save_file(content, filepath):
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Guardado: {filepath}")
    except Exception as e:
        print(f"Error al guardar {filepath}: {e}")

# Función asíncrona para descargar una página
async def fetch_page(session, url, attempt=1):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        if attempt < MAX_ATTEMPTS:
            print(f"Intento {attempt} fallido para {url}. Reintentando...")
            await asyncio.sleep(1)  # Esperar 1 segundo antes de reintentar
            return await fetch_page(session, url, attempt + 1)
        else:
            print(f"Error al descargar {url} después de {MAX_ATTEMPTS} intentos: {e}")
            return None

# Función asíncrona para extraer CSS y guardar metadatos
async def extract_css(session, url, output_folder, metadata, depth=0):
    if depth > MAX_DEPTH:
        print(f"Profundidad máxima alcanzada para {url}. Deteniendo rastreo.")
        return

    try:
        html = await fetch_page(session, url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')
        domain = urlparse(url).netloc
        page_folder = os.path.join(output_folder, domain, urlparse(url).path.strip("/"))
        os.makedirs(page_folder, exist_ok=True)

        # Guardar HTML
        html_file = os.path.join(page_folder, "page.html")
        save_file(html, html_file)

        # Extraer CSS en línea
        inline_css = soup.find_all('style')
        if inline_css:
            css_file = os.path.join(page_folder, "inline_styles.css")
            css_content = "\n".join(style.text for style in inline_css)
            save_file(css_content, css_file)
            metadata[url] = {"inline_css": css_file}

        # Extraer CSS externo
        for link in soup.find_all('link', rel='stylesheet'):
            css_url = urljoin(url, link['href'])
            css_filename = os.path.basename(urlparse(css_url).path)
            css_file = os.path.join(page_folder, css_filename)

            # Descargar CSS externo
            css_content = await fetch_page(session, css_url)
            if css_content:
                save_file(css_content, css_file)
                if url not in metadata:
                    metadata[url] = {}
                metadata[url]["external_css"] = metadata[url].get("external_css", []) + [css_file]

        # Guardar metadatos
        with open(metadata_file, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)

        # Buscar enlaces internos y seguir rastreando
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if full_url.startswith(base_url) and full_url not in metadata:
                await extract_css(session, full_url, output_folder, metadata, depth + 1)

    except Exception as e:
        print(f"Error al procesar {url}: {e}")

# Función principal asíncrona
async def main():
    check_robots_txt()

    async with aiohttp.ClientSession() as session:
        await extract_css(session, base_url, output_folder, metadata)

# Ejecutar el script
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Proceso interrumpido por el usuario. Guardando metadatos...")
        with open(metadata_file, "w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)
        print("Metadatos guardados correctamente.")