import secrets
secret_key = secrets.token_hex(32)

DB_Config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'securevault1234',
    'database': 'securevault',
    'port': 3306
}