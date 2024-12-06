import os
import binascii

def generate_csrf_token():
    return binascii.hexlify(os.urandom(24)).decode()