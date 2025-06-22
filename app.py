from flask import Flask, request, jsonify
import dns.resolver
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# ======= ROUTE 1: Deteksi Nameserver =======
@app.route('/nameserver', methods=['GET'])
def get_nameserver():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Parameter 'domain' wajib diisi"}), 400

    try:
        answers = dns.resolver.resolve(domain, 'NS')
        ns_records = [rdata.to_text() for rdata in answers]
        return jsonify({"domain": domain, "nameservers": ns_records})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======= ROUTE 2: Scrape Konten =======
@app.route('/scrape', methods=['GET'])
def scrape_content():
    url = request.args.get('url')
    tag = request.args.get('tag', 'p')
    class_name = request.args.get('class')  # opsional
    id_name = request.args.get('id')        # opsional

    if not url:
        return jsonify({"error": "Parameter 'url' wajib diisi"}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        if class_name:
            elements = soup.find_all(tag, class_=class_name)
        elif id_name:
            elements = soup.find_all(tag, id=id_name)
        else:
            elements = soup.find_all(tag)

        results = [el.get_text(strip=True) for el in elements]
        return jsonify({
            "url": url,
            "tag": tag,
            "results": results
        })
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request error: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"Scraping error: {e}"}), 500

# ======= Root Test =======
@app.route('/')
def index():
    return jsonify({
        "message": "Flask API aktif",
        "endpoints": {
            "/nameserver?domain=example.com": "Ambil nameserver domain",
            "/scrape?url=https://example.com&tag=p": "Scrape konten HTML"
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
