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
    'username': 'John_Admin',
    'password': 'security_officer1234',
    'email': 'jyoshwlitha@gmail.com',
    'role': 'so'
}