import utils
import logging
from core import load_config

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Iniciando processo de ingestão")

    try:
        df = utils.ingestion(load_config)
    except Exception as e:
        logging.error(f"Erro de ingestão: {e}")
        df = None

    try:
        utils.preparation(df, load_config)
        logging.info("Fim do processo de ingestão")
    except Exception as e:
        logging.error(f"Erro de preparação: {e}")