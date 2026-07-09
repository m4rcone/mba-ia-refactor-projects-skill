import logging

from config.settings import Config
from models import system_model
from middlewares.errors import ValidationError

logger = logging.getLogger(__name__)


def health():
    return {
        "status": "ok",
        "database": "connected",
        "counts": system_model.health_counts(),
        "versao": Config.APP_VERSION,
        "ambiente": Config.ENV,
    }


def reset_database():
    system_model.reset()
    logger.warning("Banco de dados resetado")
    return {"mensagem": "Banco de dados resetado", "sucesso": True}


def run_query(dados):
    sql = (dados or {}).get("sql", "")
    if not sql:
        raise ValidationError("Query não informada")
    return system_model.run_query(sql)
