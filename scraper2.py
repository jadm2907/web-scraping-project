import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL de la página a scrapear
url = "https://www.renovare.cl/"

# Hacer la solicitud HTTP
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Parsear el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraer los títulos de las entradas del blog
    # Usamos la clase 'entry-title' para encontrar los títulos
    titles = soup.find_all('h2', class_='entry-title')

    # Crear una lista con los títulos
    blog_titles = [title.text.strip() for title in titles]

    # Guardar los datos en un DataFrame de pandas
    df = pd.DataFrame(blog_titles, columns=["Título"])

    # Guardar los datos en un archivo CSV
    df.to_csv("blog_titles.csv", index=False)
    print("Datos guardados en 'blog_titles.csv'")
else:
    print(f"Error al acceder a la página: {response.status_code}")