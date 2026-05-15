import requests
import time

# ------------------------------------------------------------
# 1. Municípios da mesorregião do Sertão de Quixeramobim (CE)
# ------------------------------------------------------------
municipios = [
    {"nome": "Banabuiú", "cod_ibge": 2301851},
    {"nome": "Boa Viagem", "cod_ibge": 2302404},
    {"nome": "Choró", "cod_ibge": 2303931},
    {"nome": "Ibaretama", "cod_ibge": 2305266},
    {"nome": "Madalena", "cod_ibge": 2307635},
    {"nome": "Quixadá", "cod_ibge": 2311306},
    {"nome": "Quixeramobim", "cod_ibge": 2311405},
]

# ------------------------------------------------------------
# 2. Parâmetros fixos (Poder Executivo de municípios)
# ------------------------------------------------------------
co_poder = "E"          # Executivo
co_esfera = "M"         # Municípios
no_anexo = None         # Todos os anexos

# ------------------------------------------------------------
# 3. Variações de período, periodicidade e tipo de demonstrativo
# ------------------------------------------------------------
anos = [2024, 2025]
periodicidades = [
    {"tipo": "Q", "periodos": [1, 2, 3]},   # Quadrimestral
    {"tipo": "S", "periodos": [1, 2]},      # Semestral
]
tipos_demonstrativo = ["RGF", "RGF Simplificado"]

# ------------------------------------------------------------
# 4. Função para consultar a API
# ------------------------------------------------------------
def consultar(ano, periodicidade, periodo, tipo_demo, id_ente):
    url = (
        f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"
        f"?an_exercicio={ano}"
        f"&in_periodicidade={periodicidade}"
        f"&nr_periodo={periodo}"
        f"&co_tipo_demonstrativo={tipo_demo}"
        f"&co_poder={co_poder}"
        f"&id_ente={id_ente}"
    )
    if no_anexo:
        url += f"&no_anexo={no_anexo}"
    if co_esfera:
        url += f"&co_esfera={co_esfera}"
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        dados = resp.json()
        return dados.get("items", [])
    except Exception as e:
        print(f"Erro na consulta: {e}")
        return []

# ------------------------------------------------------------
# 5. Realizar todas as consultas e acumular estatísticas
# ------------------------------------------------------------
total_consultas = 0
total_registros = 0
max_registros = 0
consulta_max_desc = ""
registros_por_municipio = {m["nome"]: 0 for m in municipios}

for ano in anos:
    for per in periodicidades:
        for periodo in per["periodos"]:
            for tipo in tipos_demonstrativo:
                for mun in municipios:
                    total_consultas += 1
                    registros = consultar(ano, per["tipo"], periodo, tipo, mun["cod_ibge"])
                    qtd = len(registros)
                    total_registros += qtd
                    registros_por_municipio[mun["nome"]] += qtd
                    
                    if qtd > max_registros:
                        max_registros = qtd
                        consulta_max_desc = f"ano={ano}, per={per['tipo']}{periodo}, tipo={tipo}, mun={mun['nome']}"
                    
                    time.sleep(1)  # Respeitar limite da API

# ------------------------------------------------------------
# 6. Exibir respostas para o caderno
# ------------------------------------------------------------
print("=" * 50)
print("RESPOSTAS PARA O CADERNO")
print("=" * 50)

print("\n11. Como o código identifica os municípios desejados?")
print("    -> Pelo código IBGE de cada município, fornecido no parâmetro 'id_ente'.")

print(f"\n12. Quantas consultas foram realizadas à API?")
print(f"    -> {total_consultas} consultas.")

print("\n13. Qual consulta retornou o maior número de registros e quantos registros?")
print(f"    -> Consulta: {consulta_max_desc}")
print(f"    -> Registros: {max_registros}")

print(f"\n14. Quantos registros foram coletados no total?")
print(f"    -> {total_registros} registros.")

print("\n15. Houve diferenças na quantidade de registros entre os municípios?")
print("    Registros por município:")
    for nome, qtd in registros_por_municipio.items():
        print(f"       {nome}: {qtd}")
    
    if len(set(registros_por_municipio.values())) > 1:
        print("    -> SIM, houve diferenças.")
        print("    Possíveis causas:")
        print("       - Municípios com menos de 50 mil habitantes podem usar RGF Simplificado (periodicidade semestral), gerando menos registros.")
        print("       - Nem todos os municípios enviam todos os anexos ou períodos para o SICONFI.")
        print("       - Diferenças no porte e na complexidade da gestão fiscal.")
    else:
        print("    -> NÃO, todos os municípios tiveram a mesma quantidade.")