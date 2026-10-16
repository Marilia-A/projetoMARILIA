_estado = {"usuario": None}


def entrar(usuario: dict):
    _estado["usuario"] = usuario


def sair():
    _estado["usuario"] = None


def usuario() -> dict | None:
    return _estado["usuario"]


def pode_gerenciar() -> bool:
    u = _estado["usuario"]
    return bool(u) and u["tipo"] in ("professor", "admin")


def eh_admin() -> bool:
    u = _estado["usuario"]
    return bool(u) and u["tipo"] == "admin"