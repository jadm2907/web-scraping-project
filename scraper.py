import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de la página a scrapear
url = "https://example.com"  # Cambia esto por la URL que desees scrapear

# Hacer la solicitud HTTP
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraer los títulos de las noticias (ajusta el selector según la página)
    titles = soup.find_all('h2')  # Cambia 'h2' por el tag correcto

    # Crear una lista con los títulos
    news_titles = [title.text.strip() for title in titles]

    # Guardar los datos en un DataFrame de pandas
    df = pd.DataFrame(news_titles, columns=["Título"])

    # Guardar los datos en un archivo CSV
    df.to_csv("news_titles.csv", index=False)
    print("Datos guardados en 'news_titles.csv'")
else:
    print(f"Error al acceder a la página: {response.status_code}")