from flask import Flask, request, render_template, redirect, url_for, session
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Observação, textos dentro de before e ou after não podem ser alterados....
CENSORED_WORD = "[palavra censurada]"
substitution_dict = {
    'encerramento': CENSORED_WORD,
    'acolhida': CENSORED_WORD,
    'institucional': CENSORED_WORD,
    'cgti': CENSORED_WORD,
    "coronavírus": CENSORED_WORD,
    "universidade": CENSORED_WORD,
    "participe": CENSORED_WORD,
    # Adicione mais palavras a serem substituídas conforme necessário
}

def replace_words(text):
    for original_word, replacement_word in substitution_dict.items():
        text = re.sub(r'\b{}\b'.format(re.escape(original_word)), replacement_word, text, flags=re.IGNORECASE)
    return text

@app.route('/')
def index():
    if not session.get('age'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['age'] = request.form['age']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('age', None)
    return redirect(url_for('index'))

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    if request.method == 'POST':
        site = request.form.get('site', '')
        if site:
            return redirect(url_for('show_proxy', site=site))
    return redirect(url_for('index'))

@app.route('/proxy/<path:site>')
def show_proxy(site):
    print(site)
    try:
        response = requests.get(site)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Encontrar todas as tags 'a' com o atributo 'href'
        for a_tag in soup.find_all('a', href=True):
            # Adicione seu servidor proxy à frente do URL usando urljoin
            if a_tag['href'].startswith('/'):
                a_tag['href'] = "http://localhost:3000/proxy/" + site + a_tag['href']
            elif a_tag['href']:
                a_tag['href'] = "http://localhost:3000/proxy/" + a_tag['href']
            
        if session.get('age') and int(session.get('age')) < 18:
            for tag in soup.find_all(['p','a','header','footer' ,'nav','span', 'div','h1','h2','h3','h4','h5','h6'], string=True):
                tag.string = replace_words(tag.get_text())
        # Retornar a página HTML modificada
        return str(soup)
    except requests.exceptions.RequestException as e:
        return str(e)

if __name__ == '__main__':
    app.run(host='localhost', port=3000)
