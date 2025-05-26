import os
import re
from flask import Flask, request, render_template
from transformers import pipeline
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import docx
import time


# Configura la ruta de Tesseract si estás en Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
clasificador = pipeline("text-classification", model="unitary/toxic-bert")

# Lista personalizada de palabras ofensivas
palabras_ofensivas_personalizadas = ["idiota", "imbécil", "estúpido", "maldito", "tonto", "grosero","perra",
                                     "ratón", "cabrón", "hijo de puta", "mierda", "pendejo", "puto", "zorra",
                                     "gilipollas", "cabrón", "coño", "puta", "maricón", "putita", "pendeja",
                                     "huevón", "pendejito", "pendejita", "pendejín", "pendejona", "pendejona",
                                     "pendejita", "pendejín", "pendejona", "pendejita", "pendejín", "pendejona",
                                     "ladrón", "ladróna", "ladróncillo", "ladróncilla", "ladrónzote", "ladrónzota",
                                     "lambón", "lambona", "lambón", "lambona", "lambón", "lambona", "sapo", "maldito",
                                    "maldita", "maldito", "maldito", "maldito"
                                     ] 

def detectar_personalizadas(texto, lista):
    texto_lower = texto.lower()
    return [palabra for palabra in lista if palabra in texto_lower]

def resaltar_palabras_ofensivas(texto, lista_palabras):
    for palabra in lista_palabras:
        patron = re.compile(rf'\b({re.escape(palabra)})\b', re.IGNORECASE)
        texto = patron.sub(r'<mark>\1</mark>', texto)
    return texto

def extraer_texto_imagen(ruta):
    imagen = Image.open(ruta)
    return pytesseract.image_to_string(imagen)

def extraer_texto_pdf(ruta):
    texto = ""
    with fitz.open(ruta) as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto

def extraer_texto_docx(ruta):
    texto = ""
    doc = docx.Document(ruta)
    for parrafo in doc.paragraphs:
        texto += parrafo.text + "\n"
    return texto

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""
    texto_resaltado = ""
    estado = ""
    tiempo_procesamiento = None
    personalizadas = [] 

    if request.method == "POST":
        inicio = time.time()
        archivo = request.files["archivo"]
        if archivo:
            ruta = os.path.join("uploads", archivo.filename)
            os.makedirs("uploads", exist_ok=True)
            archivo.save(ruta)

            extension = archivo.filename.lower().split(".")[-1]

            if extension in ["png", "jpg", "jpeg"]:
                texto = extraer_texto_imagen(ruta)
            elif extension == "pdf":
                texto = extraer_texto_pdf(ruta)
            elif extension == "docx":
                texto = extraer_texto_docx(ruta)
            else:
                mensaje = "❌ Tipo de archivo no soportado."
                estado = "Error"
                return render_template("index.html", mensaje=mensaje, estado=estado, texto="")

            # Análisis con BERT por fragmentos
            ofensivo = False
            detalles = []
            fragmentos_ofensivos = []
            fragmentos = [texto[i:i+512] for i in range(0, len(texto), 512)]
            for i, fragmento in enumerate(fragmentos):
                resultados = clasificador(fragmento)
                for resultado in resultados:
                    if resultado["score"] >= 0.7 and resultado["label"].lower() != "non-toxic":
                        ofensivo = True
                        detalles.append(f"Fragmento {i+1}: {resultado['label']} ({round(resultado['score']*100, 2)}%)")
                        fragmentos_ofensivos.append(fragmento)

            # Detección personalizada
            personalizadas = detectar_personalizadas(texto, palabras_ofensivas_personalizadas)
            # Resalta tanto palabras personalizadas como fragmentos detectados por BERT
            texto_resaltado = resaltar_palabras_ofensivas(texto, personalizadas + fragmentos_ofensivos)

            if ofensivo or personalizadas:
                mensaje = "❌ El archivo contiene lenguaje ofensivo.<br>"
                if detalles:
                    mensaje += "Modelo BERT detectó:<br>" + "<br>".join(detalles) + "<br>"
                if personalizadas:
                    mensaje += f"Lista personalizada detectó: {', '.join(personalizadas)}"
                estado = "Lenguaje ofensivo detectado"
            else:
                mensaje = "✅ El archivo está limpio. No se detectó lenguaje ofensivo."
                estado = "Procesado sin problemas"

            fin = time.time()
            tiempo_procesamiento = round(fin - inicio, 2)

    return render_template(
        "index.html",
        mensaje=mensaje,
        texto=texto_resaltado,
        estado=estado,
        tiempo=tiempo_procesamiento,
        palabras_detectadas=personalizadas
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)

