import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin



# ==============================================================================
# DICCIONARIO DE CLASES: Acá mapeamos qué clase usa cada diario en su cuerpo
# ==============================================================================
MAPEO_PORTALES = {
    "diariochaco.com": "body-nota",
    "datachaco.com": "body",  
}

def extraer_noticia_universal(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
    
    try:
        respuesta = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=True
        )
        if respuesta.status_code != 200:
            return {"error": f"Error de conexión: {respuesta.status_code}"}
        
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # 1. Corrección del Título: Buscamos cualquier h1 principal de la página
        titulo_tag = soup.find('h1')
        titulo = titulo_tag.get_text().strip() if titulo_tag else "Sin título"
        
        # ==============================================================================
        # DETECCIÓN DINÁMICA DE LA CLASE SEGÚN EL LINK
        # ==============================================================================
        clase_contenedor = None
        for dominio, clase in MAPEO_PORTALES.items():
            if dominio in url:
                clase_contenedor = clase
                break
        
        # 2. Cuerpo de la nota
        clase_a_buscar = clase_contenedor if clase_contenedor else 'body-nota'
        contenedor_cuerpo = soup.find('div', class_=clase_a_buscar)
        cuerpo_parrafos = []
        
        # 🛑 FRASE O COSAS QUE NO QUERÉS QUE APAREZCAN: Agregá acá las que vayan molestando
        basura = ["COMENTÁ EN FACEBOOK", "Diario Chaco, Liniers", "HACÉ CLICK ACÁ", "Seguinos en", "Compartir nota","El contenido al que quiere acceder es exclusivo para suscriptores.",
                  "TARIFARIO - MINUTOUNO", "Propietario: Desarrollos Electrónicos Informáticos S.A.", "Domicilio: Uriarte 1899. CABA", "Registro DNDA en trámite", "HABEAS SRLFrench 675, Resistencia. Chaco (3500)", "Teléfonos3624152392 / 3624152394", "E-mail[email protected]",]
        
        if contenedor_cuerpo:
            for p in contenedor_cuerpo.find_all('p'):
                texto = p.get_text().strip()
                
                # Si el párrafo contiene algo de la lista basura, lo saltea y sigue con el próximo p
                if any(frase in texto for frase in basura):
                    continue
                    
                if len(texto) > 10:
                    cuerpo_parrafos.append(texto)
        else:
            # Respaldo si no encuentra el div (Tu Plan B indestructible)
            for p in soup.find_all('p'):
                texto = p.get_text().strip()
                
                # También limpiamos la basura en el extractor genérico
                if any(frase in texto for frase in basura):
                    continue
                    
                if len(texto) > 20:
                    cuerpo_parrafos.append(texto)
                    
        # 3. Corrección de Imágenes: Buscamos imágenes dentro de la nota y la imagen destacada principal
        imagenes = []
        
        for img in soup.find_all('img'):
            src = (
                img.get('src') or 
                img.get('data-src') or 
                img.get('data-lazy-src') or 
                img.get('data-src-large') or
                img.get('srcset')
            )
            
            if src:
                if "," in src:
                    src = src.split(",")[0].strip().split(" ")[0]
                    
                src_lower = src.lower()
                if any(x in src_lower for x in ['logo', 'avatar', 'icon', 'widgets', 'banner', 'wp-content/themes']):
                    continue
                    
                if any(ext in src_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    url_completa = urljoin(url, src)
                    if url_completa not in imagenes:
                        imagenes.append(url_completa)
        
        return {
            "titulo": titulo,
            "cuerpo": cuerpo_parrafos,  
            "imagenes": imagenes[:3]
        }
        
    except Exception as e:
        return {"error": str(e)}

# ==============================================================================
# SERVIDOR FLASK
# ==============================================================================
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

@app.route('/api/extraer', methods=['POST'])
def api_extraer():
    datos_recibidos = request.json
    url = datos_recibidos.get('url')
    
    if not url:
        return jsonify({"error": "No se proporcionó una URL"}), 400
        
    resultado = extraer_noticia_universal(url)
    
    if "error" in resultado:
        return jsonify(resultado), 400
        
    return jsonify(resultado)

if __name__ == "__main__":
    print("🚀 Servidor de Capsula Webs corriendo en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)