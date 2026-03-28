import pandas as pd
import numpy as np
import requests
import utils as utils
import logging
import re
import sqlite3
from core import MultipleDataSchema
from pydantic import ValidationError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
                    

def ingestion(configs):
    """
    Função de ingestão dos dados.
    Consome dados da api: https://randomuser.me, 10 resultados por página pelo menos
    Outputs: Retorna dataframe
    """
    api_url = "https://randomuser.me/api?results=1"
    try:
        response = requests.get(api_url, timeout=30)
        data = response.json()['results']
        df = pd.json_normalize(data)
    except Exception as e:
        errors = error.json()
        logging.error(errors)
        return None

    return df


def unflatten_dict(record) -> dict:
    """Reconstroi a hierarquia do json"""
    result = {}

    for key, value in record.items():
        parts = key.split(".")
        d = result

        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d[parts[-1]] = value

    return result


def normalize_columns(df) -> pd.DataFrame:
    """Normaliza as colunas do dataframe, trocando . por _ e removendo caracteres especiais das colunas"""

    # normaliza as colunas
    df.columns = (df.columns.str.replace(".", "_", regex=False).str.lower().str.strip())

    # remove caracteres especiais das colunas
    df.columns = [re.sub(r"[^a-z0-9_]", "", col) for col in df.columns]

    return df


def cast_types(df) -> pd.DataFrame:
    """Trata os tipos de dados"""
    # data
    df["dob_date"] = pd.to_datetime(df["dob_date"], errors="coerce")
    df["registered_date"] = pd.to_datetime(df["registered_date"], errors="coerce")

    # inteiros
    df["dob_age"] = pd.to_numeric(df["dob_age"], errors="coerce").astype("Int64")
    df["registered_age"] = pd.to_numeric(df["registered_age"], errors="coerce").astype("Int64")

    # float
    df["location_coordinates_latitude"] = pd.to_numeric(df["location_coordinates_latitude"], errors="coerce")
    df["location_coordinates_longitude"] = pd.to_numeric(df["location_coordinates_longitude"], errors="coerce")

    return df


def standardize_values(df) -> pd.DataFrame:
    """Normaliza os campos de telefone e celular"""
    # remove traços de telefone
    df["phone"] = df["phone"].str.replace(r"[^\d]", "", regex=True)
    df["cell"] = df["cell"].str.replace(r"[^\d]", "", regex=True)

    return df


def save_sqlite(df) -> pd.DataFrame:
    """Salva conteudo no banco SQLite"""
    conn = sqlite3.connect("assets/database.db")

    df.to_sql("users", conn, if_exists="append", index=False)

    df_consulta = pd.read_sql('select * from users', conn)

    conn.commit()
    conn.close()

    return df_consulta


def validation_inputs(df, configs):
    """
    Função de validação dos dados antes de salvar no banco de dados
    Output: Se não estiver no padrão correto interrompe o processo e salva alerta em 
    um arquivo de logs. Se estiver correto, salva log com mensagem: 'Dados corretos'
    """

    # substitui NaN
    records=df.replace({np.nan: None}).to_dict(orient="records")

    # reconstroi estrutura JSON
    records_nested = [unflatten_dict(r) for r in records]

    # validação PyDantic
    try:
        MultipleDataSchema(inputs_raw=records_nested)
    except ValidationError as error:
        errors = error.json()
        logging.error(errors)
        raise ValueError("Inputs out of standard, review your raw data")

    return df


def preparation(df, configs):
    """
    Função de preparação dos dados: 
        - Renomeia colunas
        - Ajusta tipo dos dados
        - Remove caracter especial
    Outputs: Salva dados tratados em base sqlite no diretorio assets
    """
    
    if df is None:
        raise ValueError("DataFrame vazio")

    # Validação
    data = validation_inputs(df, configs)

    # Transformação
    data = normalize_columns(df=data)
    data = cast_types(df=data)
    data = standardize_values(df=data)

    # # Salva no BD
    res = save_sqlite(df=data)
    print(res)
    return True

