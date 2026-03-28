# ProjetoDE – Pipeline de Ingestão e Validação de Dados

## Visão Geral

Este projeto implementa um pipeline de dados simples:

* Ingestão de dados via API pública
* Validação com schema tipado
* Tratamento e padronização dos dados
* Persistência em banco SQLite
* Verificação de qualidade dos dados

A solução simula um fluxo real de ingestão.

---

## Arquitetura do Projeto

```
ProjetoDE/
│
├── assets/
│   ├── app.log
│   ├── config.yml
│   └── database.db
│
├── src/
│   ├── app.py
│   ├── core.py
│
├── utils.py
├── requirements.txt
├── tox.ini
└── README.md
```

---

## Fluxo do Pipeline

1. **Ingestão**

   * Consome dados da API: https://randomuser.me
   * Normaliza JSON em DataFrame

2. **Validação**

   * Reconstrói estrutura hierárquica (unflatten)
   * Valida com schema Pydantic

3. **Preparação**

   * Renomeia colunas
   * Ajusta tipos de dados
   * Remove caracteres indesejados
   * Padroniza valores

4. **Persistência**

   * Salva os dados tratados em SQLite

5. **Validação pós-carga**

   * Queries SQL para checagem de qualidade

---

## Como Executar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 2. Executar pipeline

```bash
python src/app.py
```

---

## Ingestão de Dados

A função `ingestion()`:

* Consome a API
* Converte JSON em DataFrame
* Utiliza `pandas.json_normalize`

---

## Validação de Dados

A validação é feita com Pydantic:

* Estrutura tipada (schema)
* Suporte a dados aninhados
* Tratamento de inconsistências

### Exemplo de validação:

```python
MultipleDataSchema(inputs_raw=records_nested)
```

---

## Preparação dos Dados

### Renomeação de colunas

* Substitui `.` por `_`
* Converte para lowercase
* Remove caracteres especiais

### Ajuste de tipos

* Datas → `datetime`
* Inteiros → `Int64` (nullable)
* Floats → `float`

### Limpeza

* Remove espaços extras
* Normaliza telefone (apenas números)
* Padroniza strings

---

## Persistência (SQLite)

Os dados são salvos em:

```
assets/database.db
```

Tabela:

```
users
```

---

## Queries de Validação

### Ver dados

```sql
SELECT * FROM users LIMIT 10;
```

### Contagem de registros

```sql
SELECT COUNT(*) FROM users;
```

### Verificar nulos

```sql
SELECT COUNT(*) - COUNT(email) FROM users;
```

### Validar telefones

```sql
SELECT * FROM users WHERE phone LIKE '%-%';
```

---

## Configuração

O projeto suporta configuração via `config.yml`:

```yaml
data_config:
  date_columns:
    - dob_date
    - registered_date
```