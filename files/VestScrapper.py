import requests
from bs4 import BeautifulSoup as bs


#fazendo um webscrapping de uma página da web
def scrap(web_page, output_file):
    page = requests.get(web_page)
    forma_html = page.content

    soup = bs(forma_html, 'html.parser')
    texto = soup.find_all(text=True)

    #escrevendo no arquivo texto.
    with open(output_file, 'a', encoding='utf-8') as file:
        for content in texto:
            try:
                file.write(content.get_text().encode(encoding="utf-8", errors = 'replace').decode('utf-8') + '\n')
            
            except Exception as e:
                print(e)

