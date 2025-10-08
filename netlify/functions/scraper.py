import requests
from bs4 import BeautifulSoup
import json

def handler(event, context):
    """
    Esta es la función que Netlify ejecutará.
    """
    serie = event['queryStringParameters'].get('serie')

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

    try:
        # ---- CAMBIO 1: Añadir un User-Agent para simular un navegador ----
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Hacemos la petición con el User-Agent y un timeout más seguro (8s)
        response = requests.get(target_url, headers=headers, timeout=8)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        modelos_extraidos = []
        
        # ---- CAMBIO 2: Usar el selector HTML correcto ----
        # La lista de productos está en un <ul> con la clase 'products-grid'
        product_list = soup.find('ul', class_='products-grid')
        
        if product_list:
            # Cada modelo está en un <li> dentro de la lista
            for item in product_list.find_all('li', class_='item'):
                # El enlace está dentro de un <h2> y luego un <a>
                link_tag = item.find('h2', class_='product-name').find('a')
                if link_tag:
                    modelos_extraidos.append({
                        'nombre': link_tag.get('title'),
                        'url': link_tag.get('href')
                    })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'modelos': modelos_extraidos})
        }

    except requests.RequestException as e:
        # Este bloque se activa si hay un error de red o timeout
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Error de conexión o timeout: {str(e)}"})
        }
    except Exception as e:
        # Este bloque captura cualquier otro error en el scraping
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Error durante el scraping: {str(e)}"})
        }
