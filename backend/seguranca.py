import hashlib
import hmac
import secrets

ITERACOES = 600_000


def gerar_hash(senha: str) -> str:
    sal = secrets.token_bytes(16)
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, ITERACOES)
    return f"{sal.hex()}${resumo.hex()}"


def verificar_senha(senha: str, senha_hash: str) -> bool:
    sal_hex, resumo_hex = senha_hash.split("$")
    resumo = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal_hex), ITERACOES)
    return hmac.compare_digest(resumo.hex(), resumo_hex)