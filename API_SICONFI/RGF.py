#Consulta a API SICONFI para extrair dados relacionados ao RGF
#Código de Alissa Garcia Moreira ADS S4
#Ciência de Dados - Magno Prudêncio

import requests
import pandas as pd
import time

BASE_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"

# Periodicidade:
# Q = Quadrimestral
# S = Semestral
PERIODICIDADES = ["Q", "S"]

# Períodos possíveis
# Q -> 1,2,3
# S -> 1,2
PERIODOS = {
    "Q": [1, 2, 3],
    "S": [1, 2]
}

# Tipos de poder
PODERES = ["E", "L", "J", "M", "D"]

# Esferas
ESFERAS = ["M", "E", "U", "C"]

# Intervalo de anos
ANOS = range(2014, 2026)

def obter_entes():
    """
    Coleta os entes disponíveis na API de municípios.
    """

    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/entes"

    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()

        # Algumas respostas vêm dentro de "items"
        if "items" in dados:
            return dados["items"]

    return []

def coletar_rgf():

    dados_rgf = []

    entes = obter_entes()

    print(f"Total de entes encontrados: {len(entes)}")

    for ente in entes:

        try:
            id_ente = ente["id_ente"]
        except:
            continue

        for ano in ANOS:

            for periodicidade in PERIODICIDADES:

                for periodo in PERIODOS[periodicidade]:

                    for poder in PODERES:

                        params = {
                            "an_exercicio": ano,
                            "in_periodicidade": periodicidade,
                            "nr_periodo": periodo,
                            "co_tipo_demonstrativo": "RGF",
                            "co_poder": poder,
                            "id_ente": id_ente
                        }

                        try:

                            response = requests.get(
                                BASE_URL,
                                params=params,
                                timeout=30
                            )

                            if response.status_code == 200:

                                json_data = response.json()

                                if "items" in json_data:

                                    items = json_data["items"]

                                    for item in items:

                                        dados_rgf.append({

                                            "exercicio": item.get("exercicio"),
                                            "periodo": item.get("periodo"),
                                            "periodicidade": item.get("periodicidade"),
                                            "instituicao": item.get("instituicao"),
                                            "cod_ibge": item.get("cod_ibge"),
                                            "uf": item.get("uf"),
                                            "co_poder": item.get("co_poder"),
                                            "populacao": item.get("populacao"),
                                            "anexo": item.get("anexo"),
                                            "rotulo": item.get("rotulo"),
                                            "coluna": item.get("coluna"),
                                            "cod_conta": item.get("cod_conta"),
                                            "conta": item.get("conta"),
                                            "valor": item.get("valor")

                                        })

                            print(
                                f"OK | Ente: {id_ente} "
                                f"| Ano: {ano} "
                                f"| Periodo: {periodo}"
                            )

                            # Pequena pausa para evitar bloqueio
                            time.sleep(0.2)

                        except Exception as erro:

                            print(
                                f"ERRO | Ente: {id_ente} "
                                f"| Ano: {ano} "
                                f"| Periodo: {periodo}"
                            )

                            print(erro)

    return dados_rgf

dados = coletar_rgf()

df = pd.DataFrame(dados)

df.to_csv(
    "dados_rgf_completo.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nColeta finalizada com sucesso!")
print(f"Total de registros coletados: {len(df)}")