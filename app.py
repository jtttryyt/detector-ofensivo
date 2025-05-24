import os
from flask import Flask, request, render_template
from transformers import pipeline
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import docx

# Configura la ruta de Tesseract si estás en Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)
clasificador = pipeline("text-classification", model="unitary/toxic-bert")

# Lista personalizada de palabras ofensivas
palabras_ofensivas_personalizadas = ["idiota", "imbécil", "estúpido", "maldito", "tonto", "grosero"]

# Función para detectar palabras ofensivas propias
def detectar_personalizadas(texto, lista):
    texto_lower = texto.lower()
    return [palabra for palabra in lista if palabra in texto_lower]

# Función para extraer texto de imágenes
def extraer_texto_imagen(ruta):
    imagen = Image.open(ruta)
    return pytesseract.image_to_string(imagen)

# Función para extraer texto de PDF
def extraer_texto_pdf(ruta):
    texto = ""
    with fitz.open(ruta) as doc:
        for pagina in doc:
            texto += pagina.get_text()
    return texto

# Función para extraer texto de DOCX
def extraer_texto_docx(ruta):
    texto = ""
    doc = docx.Document(ruta)
    for parrafo in doc.paragraphs:
        texto += parrafo.text + "\n"
    return texto

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""
    detalles = []

    if request.method == "POST":
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
                return render_template("index.html", mensaje=mensaje)

            # Análisis con BERT
            resultados = clasificador(texto[:512])
            ofensivo = False
            for resultado in resultados:
                if resultado["score"] >= 0.7 and resultado["label"].lower() != "non-toxic":
                    ofensivo = True
                    detalles.append(f"{resultado['label']} ({round(resultado['score']*100, 2)}%)")

            # Análisis personalizado
            personalizadas = detectar_personalizadas(texto, palabras_ofensivas_personalizadas)

            if ofensivo or personalizadas:
                mensaje = "❌ El archivo contiene lenguaje ofensivo.<br>"
                if detalles:
                    mensaje += f"Modelo BERT detectó: {', '.join(detalles)}<br>"
                if personalizadas:
                    mensaje += f"Lista personalizada detectó: {', '.join(personalizadas)}"
            else:
                mensaje = "✅ El archivo está limpio. No se detectó lenguaje ofensivo."

    return render_template("index.html", mensaje=mensaje)
if __name__ == "__main__":
    app.run(debug=True)
