import requests
import csv
from requests.auth import HTTPBasicAuth

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DNAC_URL = "https://sandboxdnac.cisco.com"
USER = "devnetuser"
PASS = "Cisco123!"

def obtener_token():
    print("Autenticando con Cisco DNA Center...")
    url_auth = f"{DNAC_URL}/dna/system/api/v1/auth/token"
    
    try:
        respuesta = requests.post(url_auth, auth=HTTPBasicAuth(USER, PASS), verify=False)
        respuesta.raise_for_status()
        token = respuesta.json()['Token']
        print("¡Token obtenido con éxito!")
        return token
    except Exception as e:
        print(f"Error al obtener el token: {e}")
        return None

def obtener_inventario(token):
    print("Solicitando inventario de dispositivos...")
    url_devices = f"{DNAC_URL}/dna/intent/api/v1/network-device"
    
    headers = {
        "Accept": "application/json",
        "X-Auth-Token": token
    }

    try:
        respuesta = requests.get(url_devices, headers=headers, verify=False)
        respuesta.raise_for_status() 
        datos = respuesta.json()
        return datos['response']
    except Exception as e:
        print(f"Error al obtener el inventario: {e}")
        return None

def guardar_en_csv(dispositivos):
    if not dispositivos:
        print("No hay dispositivos para guardar.")
        return
    
    archivo = 'inventario.csv'
    with open(archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Hostname', 'Familia', 'IP de Gestión', 'MAC Address'])
        
        for dev in dispositivos:
            writer.writerow([
                dev.get('hostname', 'N/A'),
                dev.get('family', 'N/A'),
                dev.get('managementIpAddress', 'N/A'),
                dev.get('macAddress', 'N/A')
            ])
    print(f"¡Éxito! Datos exportados correctamente a {archivo}")

if __name__ == "__main__":
    token = obtener_token()
    if token:
        inventario = obtener_inventario(token)
        guardar_en_csv(inventario)