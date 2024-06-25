import json
import os

def process_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    required_nodes = ['identificacion', 'emisor', 'receptor']  # Verification Nodes
    if all(node in data for node in required_nodes):
        generation_code = data['identificacion'].get('codigoGeneracion')  
        new_file_path = os.path.join(os.path.dirname(file_path), f"{generation_code}.json")
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        os.rename(file_path, new_file_path)
        print(f"File renamed to {new_file_path}")
        return data  
    else:
        os.remove(file_path)
        print(f"File {file_path} removed due to lack of required nodes")
        return None
