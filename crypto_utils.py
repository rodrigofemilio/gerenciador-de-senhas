#############################
# Imports
#############################

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

#############################
# Funções de Criptografia
#############################

# Gera uma chave a partir da senha mestra usando PBKDF2HMAC
def gerar_chave_from_senha(senha_mestra: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(senha_mestra.encode()))
    return key

# Criptografa senha para armazenamento seguro
def criptografar(texto: str, chave: bytes) -> str:
    """Criptografa um texto"""
    f = Fernet(chave)
    texto_criptografado = f.encrypt(texto.encode())
    return texto_criptografado.decode()

# Descriptografa senha para uso
def descriptografar(texto_criptografado: str, chave: bytes) -> str:
    """Descriptografa um texto"""
    f = Fernet(chave)
    texto = f.decrypt(texto_criptografado.encode())
    return texto.decode()

# Gera um salt aleatório
def gerar_salt() -> bytes:
    return os.urandom(16)