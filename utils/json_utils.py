import json
import os
from utils.db_utils import *


def process_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    required_nodes = ['identificacion', 'emisor', 'receptor']
    if all(node in data for node in required_nodes):
        # Data for database
        generation_code = data['identificacion']['codigoGeneracion']
        # Extra Data
        control_number = data['identificacion']['numeroControl']
        receiver_name = data['receptor']['nombre']
        issuer_name = data['emisor']['nombre']
        issuer_nit = data['emisor']['nit']
        issuer_nrc = data['emisor']['nrc']
        date = data['identificacion']['fecEmi']
        json_path = f'static/{generation_code}.json'
        pdf_path = f'static/{generation_code}.pdf'
        # Check if the generation code already exists
        if check_generation_code_exists(generation_code):
            os.remove(file_path)
            return None
        
        
        # List Data For Send DB
        InsertInformation(generation_code, control_number, receiver_name, issuer_name, issuer_nit, issuer_nrc, date, json_path, pdf_path)
        new_file_path = os.path.join(os.path.dirname(file_path), f"{generation_code}.json")
        os.rename(file_path, new_file_path)
        print(f"Archivo renombrado a {new_file_path}")
        return generation_code
    else:
        os.remove(file_path)
        print(f"Archivo {file_path} eliminado por falta de nodos requeridos")
        return None
