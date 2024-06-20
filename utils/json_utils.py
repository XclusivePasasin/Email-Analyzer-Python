import json
import os

def process_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    required_nodes = ['identificacion', 'emisor', 'receptor']
    if all(node in data for node in required_nodes):
        codigo_generacion = data['identificacion']['codigoGeneracion']
        new_file_path = os.path.join(os.path.dirname(file_path), f"{codigo_generacion}.json")
        os.rename(file_path, new_file_path)
        print(f"Archivo renombrado a {new_file_path}")
        return codigo_generacion
    else:
        os.remove(file_path)
        print(f"Archivo {file_path} eliminado por falta de nodos requeridos")
        return  None

