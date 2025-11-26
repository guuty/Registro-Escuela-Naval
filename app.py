from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# ===== CONFIGURAR TU EMAIL =====
EMAIL_REMITENTE = "gustavoleonelferreyra@gmail.com"
EMAIL_PASSWORD = "hjpt zefw sstb rqfu"  # NO tu clave normal
EMAIL_DESTINO = "ematevez@gmail.com"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Scraper Educativo</title>
</head>
<body style="font-family: Arial; padding: 20px;">
    <h1>🔎 Scraper educativo</h1>

    <form method="post">
        <input type="text" name="keyword" placeholder="Ingresá una palabra" required>
        <button type="submit">Buscar</button>
    </form>

    {% if results %}
        <h2>📋 Resultados</h2>
        <table border="1" cellpadding="5">
            <tr>
                <th>Título</th>
                <th>Link</th>
            </tr>
            {% for title, link in results %}
            <tr>
                <td>{{ title }}</td>
                <td><a href="{{ link }}" target="_blank">{{ link }}</a></td>
            </tr>
            {% endfor %}
        </table>
        <p>✅ Resultados enviados por email</p>
    {% endif %}
</body>
</html>
"""

def enviar_email(contenido):
    msg = MIMEText(contenido)
    msg["Subject"] = "Resultados del Scraper"
    msg["From"] = EMAIL_REMITENTE
    msg["To"] = EMAIL_DESTINO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_REMITENTE, EMAIL_PASSWORD)
        server.send_message(msg)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        keyword = request.form["keyword"]

        # URL de ejemplo (puede cambiarse)
        url = f"https://www.bing.com/search?q={keyword}"

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        # Buscar resultados
        for item in soup.select("li.b_algo h2 a")[:5]:
            title = item.text
            link = item["href"]
            results.append((title, link))

        # Preparar email
        contenido_email = "Resultados del scraping:\n\n"
        for title, link in results:
            contenido_email += f"{title}\n{link}\n\n"

        enviar_email(contenido_email)

    return render_template_string(HTML, results=results)

if __name__ == "__main__":
    app.run(debug=True)
