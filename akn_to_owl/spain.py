import requests

def download_document(origin):
    try:
        response = requests.get(origin, stream=True)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {origin}: {e}")
        return None

def main():
    
    base_url = 'http://api.boeapi.com/v1/documento/'
    identificador = 'BOE-A-1996-8930'
    # Compone la url con el identificador del documento

    url = base_url + "?identificator=" + identificador
    # Add ?format=json to the url to get the json response
    url += "&format=xml"


    # Make a get request
    response = requests.get(url)

    # Save the response as a json file
    with open('data/akn/BOE-A-1996-8930.xml', 'wb') as file:
        file.write(response.content)
    
    print(response.status_code)
    print(response.text)

if __name__ == '__main__':
    main()
