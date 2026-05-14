import requests
from bs4 import BeautifulSoup
import pandas as pd
def get_total_pages(base_url):
    response = requests.get(base_url)
    response.encoding = "utf-8"
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        pager = soup.find("ul", class_="pager")
        if pager:
            last_page = pager.find("li", class_="current").text.strip().split()[-1]
            return int(last_page)
    return 1

def scrape_books(base_url):
    total_pages = get_total_pages(base_url)
    book_list = []
    for page in range(1, total_pages + 1):
        url = f"{base_url}/catalogue/page-{page}.html"
        response = requests.get(url)
        response.encoding = "utf-8"
        
        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

    for book in books:
        title = book.h3.a.attrs["title"]
        price = book.find("p", class_="price_color").text
        rating = book.p.attrs["class"][1]
        book_list.append([title, price, rating])
    return book_list

# URL base
domain = "https://books.toscrape.com"
books_data = scrape_books(domain)

# Criar um DataFrame
df = pd.DataFrame(books_data, columns=["Título", "Preço", "Classificação"])

# Salvar os dados em um arquivo CSV
df.to_csv("books__.csv", index=False, encoding="utf-8")
print("Dados extraídos com sucesso!")