import requests
from bs4 import BeautifulSoup
import pandas as pd
# URL da página alvo
url = "https://books.toscrape.com/"

# Fazer a requisição HTTP
response = requests.get(url)
response.encoding = "utf-8" # Define a codificação

# Verificar se a requisição foi bem-sucedida
if response.status_code == 200:
# Criar o objeto BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")
# Extrair informações
    books = soup.find_all("article", class_="product_pod")
    book_list = []

    for book in books:
        title = book.h3.a.attrs["title"]
        price = book.find("p", class_="price_color").text
        rating = book.p.attrs["class"][1]
        book_list.append([title, price, rating])

# Criar um DataFrame
    df = pd.DataFrame(book_list, columns=["Título", "Preço", "Classificação"])

# Salvar os dados em um arquivo .csv
    df.to_csv("books.csv", index=False)

# Exibir os dados
    print(df)

else:
    print("Erro ao acessar a página")