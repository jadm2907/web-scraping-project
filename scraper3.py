import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

# URL base del sitio web
base_url = "https://www.renovare.cl/"

# Conjunto para almacenar las URLs ya visitadas
visited_urls = set()

# Lista para almacenar los datos extraídos
extracted_data = []

# Función para extraer datos de una página
def scrape_page(url):
    try:
        # Hacer la solicitud HTTP
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP

        # Parsear el contenido HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraer el título de la página
        title = soup.find('h1').text.strip() if soup.find('h1') else "Sin título"

        # Extraer el contenido de la página (por ejemplo, párrafos)
        paragraphs = [p.text.strip() for p in soup.find_all('p')]
        content = "\n".join(paragraphs)

        # Guardar los datos extraídos
        extracted_data.append({
            "URL": url,
            "Título": title,
            "Contenido": content
        })

        # Buscar enlaces internos y seguir rastreando
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)  # Convertir enlace relativo a absoluto

            # Verificar si el enlace es del mismo dominio y no ha sido visitado
            if full_url.startswith(base_url) and full_url not in visited_urls:
                visited_urls.add(full_url)
                scrape_page(full_url)  # Llamada recursiva para rastrear la nueva URL

    except Exception as e:
        print(f"Error al procesar {url}: {e}")

# Iniciar el rastreo desde la página principal
visited_urls.add(base_url)
scrape_page(base_url)

# Guardar los datos en un archivo CSV
df = pd.DataFrame(extracted_data)
df.to_csv("renovare_full_site.csv", index=False)
print(f"Datos extraídos de {len(extracted_data)} páginas y guardados en 'renovare_full_site.csv'.")