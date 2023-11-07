from flask import Flask, request, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup
import re
app = Flask(__name__)

# Observação, textos dentro de before e ou after não podem ser alterados....
substitution_dict = {
    'encerramento': '[palavra censurada]',
    'acolhida': '[palavra censurada]',
    'buscar': '[palavra censurada]',
    'acesso': '[palavra censurada]',
    # Adicione mais palavras a serem substituídas conforme necessário
}

def replace_words(text):
    for original_word, replacement_word in substitution_dict.items():
        text = re.sub(r'\b{}\b'.format(re.escape(original_word)), replacement_word, text, flags=re.IGNORECASE)
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    if request.method == 'POST':
        site = request.form.get('site', '')
        if site:
            return redirect(url_for('show_proxy', site=site))
    return redirect(url_for('index'))

@app.route('/proxy/<path:site>')
def show_proxy(site):
    try:
        response = requests.get(site)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontrar todas as tags 'a' com o atributo 'href'
        for a_tag in soup.find_all('a', href=True):
            # Adicione seu servidor proxy à frente do URL usando urljoin
            if site in a_tag['href']:
                a_tag['href'] = "http://localhost:3000/proxy/" + a_tag['href']
            else:
              a_tag['href'] = "http://localhost:3000/proxy/" + site + a_tag['href']

        for tag in soup.find_all(['p','a','header','footer' ,'nav','span', 'div','h1','h2','h3','h4','h5','h6'], string=True):
            tag.string = replace_words(tag.get_text())

        # Retornar a página HTML modificada
        return str(soup)
    except requests.exceptions.RequestException as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='localhost', port=3000)