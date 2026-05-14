import requests
import pandas as pd
import time

# URL da API
BASE_URL = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"

municipios = {
    "Banabuiú": 2301852,
    "Boa Viagem": 2302405,
    "Choró": 2303932,
    "Ibaretama": 2305267,
    "Madalena": 2307636,
    "Quixadá": 2311307,
    "Quixeramobim": 2311406
}

# Anos desejados
anos = [2024, 2025]

# Periodicidades
periodicidades = {
    "Q": [1, 2, 3],
    "S": [1, 2]
}

# Lista para armazenar os dados
dados_rgf = []

# Loop principal
for nome_municipio, id_ente in municipios.items():

    for ano in anos:

        for periodicidade, periodos in periodicidades.items():

            for periodo in periodos:

                params = {
                    "an_exercicio": ano,
                    "in_periodicidade": periodicidade,
                    "nr_periodo": periodo,
                    "co_tipo_demonstrativo": "RGF",
                    "co_poder": "E",  # Executivo
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

                                    "municipio": nome_municipio,
                                    "exercicio": item.get("exercicio"),
                                    "periodo": item.get("periodo"),
                                    "periodicidade": item.get("periodicidade"),
                                    "instituicao": item.get("instituicao"),
                                    "anexo": item.get("anexo"),
                                    "conta": item.get("conta"),
                                    "valor": item.get("valor")

                                })

                    print(
                        f"OK | {nome_municipio} | "
                        f"{ano} | {periodo}"
                    )

                    # Pausa para evitar sobrecarga
                    time.sleep(0.2)

                except Exception as erro:

                    print(
                        f"ERRO | {nome_municipio} | "
                        f"{ano} | {periodo}"
                    )

                    print(erro)

# Criar DataFrame
df = pd.DataFrame(dados_rgf)

# Exportar CSV
df.to_csv(
    "rgf_sertao_quixeramobim_2024_2025.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo CSV gerado com sucesso!")
print(f"Total de registros: {len(df)}")