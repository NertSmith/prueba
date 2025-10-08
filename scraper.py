import requests
from bs4 import BeautifulSoup
import json

def handler(event, context):
    """
    Esta es la función que Netlify ejecutará.
    """
    # Obtenemos el parámetro 'serie' de la URL
    serie = event['queryStringParameters'].get('serie')

    # Aquí mapeamos el parámetro a la URL real
    urls = {
        'dl-series': 'https://www.harddrivesdirect.com/proliant_dl_series_servers.php',
        'ml-series': 'https://www.harddrivesdirect.com/proliant_ml_series_servers.php'
    }

    target_url = urls.get(serie)
    
    if not target_url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Serie no válida'})
        }

    # --- Aquí va tu lógica de scraping que ya conoces ---
    try:
        response = requests.get(target_url, timeout=10)
        response.raise_for_status() # Lanza un error si la petición falla
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ejemplo de extracción (debes ajustarlo a la estructura real del sitio)
        modelos_extraidos = []
        # Buscamos los enlaces dentro de un div específico, por ejemplo
        model_container = soup.find('div', class_='Category-products') 
        if model_container:
            for link in model_container.find_all('a'):
                modelos_extraidos.append({
                    'nombre': link.text.strip(),
                    'url': link['href']
                })
        
        # Devolvemos los datos en formato JSON
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'modelos': modelos_extraidos})
        }

    except requests.RequestException as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }