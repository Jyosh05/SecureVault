import secrets
secret_key = secrets.token_hex(32)

DB_Config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'securevault1234',
    'database': 'securevault',
    'port': 3306
}


so_config = {
    'username': 'JohnAdmin',
    'password': '123',
    'email': 'jyoshwlitha@gmail.com',
    'role': 'so'
}

VIRUSTOTAL_API_KEY = "09d3f2180d9e3bf9aa9b3b312ddc352fb5e4f9049d2442fd789a589e3bbc26d5"

MODEL_FILE = '../pii_model.pkl'
LABEL_ENCODER_FILE = '../pii_label_encoder.pkl'
DATA_FILE = 'test_data/pii_data.json'

