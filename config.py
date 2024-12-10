import secrets
secret_key = secrets.token_hex(32)

DB_Config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'securevault1234',
    'database': 'securevault',
    'port': 3306
}

ALLOWED_EXTENSIONS = {'pdf','txt','docx','xlsx','pptx'}


so_config = {
    'username': 'JohnAdmin',
    'password': 'security_officer1234',
    'email': 'jyoshwlitha@gmail.com',
    'role': 'so'
}