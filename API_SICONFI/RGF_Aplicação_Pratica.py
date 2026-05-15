import requests
import pandas as pd
import time
from typing import List, Dict, Any

# =============================================================================
# 1. DEFINIÇÃO DOS MUNICÍPIOS E SEUS CÓDIGOS IBGE
# =============================================================================

# Municípios da mesorregião do Sertão de Quixeramobim (CE)
municipios = [
    {"nome": "Banabuiú", "cod_ibge": 2301851},
    {"nome": "Boa Viagem", "cod_ibge": 2302404},
    {"nome": "Choró", "cod_ibge": 2303931},
    {"nome": "Ibaretama", "cod_ibge": 2305266},
    {"nome": "Madalena", "cod_ibge": 2307635},
    {"nome": "Quixadá", "cod_ibge": 2311306},
    {"nome": "Quixeramobim", "cod_ibge": 2311405},
]

# Parâmetros fixos para todos os cenários
poder = "E"  # Poder Executivo
esfera = "M"  # Municípios

# Campos opcionais (para não filtrar anexos específicos)
no_anexo = None
co_esfera = None

# Períodos e periodicidades possíveis
# Q = quadrimestral
# S = semestral
periodicidades = [
    {"tipo": "Q", "periodos": [1, 2, 3]},
    {"tipo": "S", "periodos": [1, 2]},
]

# Tipos de demonstrativo
tipos_demonstrativo = [
    "RGF",
    "RGF Simplificado"
]

# =============================================================================
# 2. FUNÇÃO PARA CONSULTAR A API RGF
# =============================================================================

def consultar_rgf(
    an_exercicio: int,
    in_periodicidade: str,
    nr_periodo: int,
    co_tipo_demonstrativo: str,
    co_poder: str,
    id_ente: int,
    no_anexo: str = None,
    co_esfera: str = None,
) -> List[Dict[str, Any]]:

    """
    Consulta os dados do RGF para um determinado município e período.
    """

    # Montar a URL com os parâmetros obrigatórios
    url = (
        f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"
        f"?an_exercicio={an_exercicio}"
        f"&in_periodicidade={in_periodicidade}"
        f"&nr_periodo={nr_periodo}"
        f"&co_tipo_demonstrativo={co_tipo_demonstrativo}"
        f"&co_poder={co_poder}"
        f"&id_ente={id_ente}"
    )

    # Adicionar parâmetros opcionais
    if no_anexo:
        url += f"&no_anexo={no_anexo}"

    if co_esfera:
        url += f"&co_esfera={co_esfera}"

    print(f"Consultando: {url}")

    try:

        response = requests.get(url)

        # Levanta exceção para erros HTTP
        response.raise_for_status()

        data = response.json()

        return data.get("items", [])

    except requests.exceptions.RequestException as e:

        print(f"Erro na consulta: {e}")

        return []

# =============================================================================
# 3. REALIZAR AS CONSULTAS E CONSOLIDAR OS DADOS
# =============================================================================

# Estrutura para armazenar todos os registros coletados
todos_registros = []

# Contador de consultas realizadas
total_consultas = 0

# Dicionário para armazenar a contagem de registros por consulta
registros_por_consulta = {}

# Iterar sobre todas as combinações de parâmetros
for ano in [2024, 2025]:

    for periodicidade in periodicidades:

        for periodo in periodicidade["periodos"]:

            for tipo_demonstrativo in tipos_demonstrativo:

                for municipio in municipios:

                    # Incrementa contador
                    total_consultas += 1

                    # Realiza consulta
                    registros = consultar_rgf(
                        an_exercicio=ano,
                        in_periodicidade=periodicidade["tipo"],
                        nr_periodo=periodo,
                        co_tipo_demonstrativo=tipo_demonstrativo,
                        co_poder=poder,
                        id_ente=municipio["cod_ibge"],
                        no_anexo=no_anexo,
                        co_esfera=co_esfera,
                    )

                    # Armazenar registros
                    for reg in registros:

                        reg["ano"] = ano
                        reg["periodicidade"] = periodicidade["tipo"]
                        reg["periodo"] = periodo
                        reg["tipo_demonstrativo"] = tipo_demonstrativo
                        reg["municipio_nome"] = municipio["nome"]
                        reg["municipio_cod_ibge"] = municipio["cod_ibge"]

                        todos_registros.append(reg)

                    # Registrar quantidade retornada
                    chave_consulta = (
                        f"{ano}-"
                        f"{periodicidade['tipo']}-"
                        f"{periodo}-"
                        f"{tipo_demonstrativo}-"
                        f"{municipio['nome']}"
                    )

                    registros_por_consulta[chave_consulta] = len(registros)

                    # Espera entre requisições
                    time.sleep(1)

# =============================================================================
# 4. CONVERTER PARA DATAFRAME E EXPORTAR CSV
# =============================================================================

# Criar DataFrame
df = pd.DataFrame(todos_registros)

# Salvar CSV
df.to_csv(
    "dados_rgf_mesorregiao_sertao_quixeramobim.csv",
    index=False,
    encoding="utf-8-sig"
)

print(
    f"\nArquivo "
    f"'dados_rgf_mesorregiao_sertao_quixeramobim.csv' "
    f"salvo com {len(df)} registros."
)