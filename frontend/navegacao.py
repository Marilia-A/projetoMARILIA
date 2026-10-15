_estado = {"page": None, "telas": {}}


def configurar(page, telas: dict):
    _estado["page"] = page
    _estado["telas"] = telas


def ir(nome: str, **params):
    _estado["telas"][nome](_estado["page"], **params)