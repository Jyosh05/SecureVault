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

VIRUSTOTAL_API_KEY = "78f01c22afe0a0839aa33bff147d32ed2133c82034f595404108f0469523a9af"

MODEL_FILE = 'pii_model.pkl'
LABEL_ENCODER_FILE = 'pii_label_encoder.pkl'
DATA_FILE = 'test_data/pii_data.json'

