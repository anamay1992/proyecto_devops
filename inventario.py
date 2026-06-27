import requests
import json
import csv

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def obtener_inventario():
    api_url = "https://sandboxdnac.cisco.com/dna/intent/api/v1/network-device"
    
    headers = {
        "Accept": "application/json",
        "X-Auth-Token": "TU_TOKEN_AQUI"
    }

    try:
        response = requests.get(api_url, headers=headers, verify=False)
        
        response.raise_for_status() 
        
        datos = response.json()
        print("Inventario obtenido exitosamente.")
        return datos['response']

    except requests.exceptions.HTTPError as errh:
        print(f"Error HTTP: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error de Conexión: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout: {errt}")
    except Exception as err:
        print(f"Ocurrió un error inesperado: {err}")
    
    return None

def guardar_en_csv(dispositivos):
    if not dispositivos:
        return
    
    with open('inventario.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Hostname', 'Tipo', 'IP de Gestión', 'MAC Address'])
        
        for dev in dispositivos:
            writer.writerow([
                dev.get('hostname', 'N/A'),
                dev.get('type', 'N/A'),
                dev.get('managementIpAddress', 'N/A'),
                dev.get('macAddress', 'N/A')
            ])
    print("Datos exportados a inventario.csv")

if __name__ == "__main__":
    inventario = obtener_inventario()
    guardar_en_csv(inventario)
