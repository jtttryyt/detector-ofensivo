# Detector de Lenguaje Ofensivo

Este proyecto es una herramienta web para detectar y resaltar lenguaje ofensivo en archivos de texto, imágenes, PDF y DOCX, usando modelos de lenguaje y una lista personalizada de palabras ofensivas en español.

---

## Características

- **Detección automática** de lenguaje ofensivo usando un modelo BERT.
- **Lista personalizada** de palabras ofensivas en español.
- **Extracción de texto** desde imágenes (OCR), PDF y archivos DOCX.
- **Resaltado visual** de palabras y fragmentos ofensivos en el texto.
- **Interfaz web** sencilla y fácil de usar.

---

## Requisitos

- Python 3.8 o superior
- pip
- Tesseract OCR (para imágenes)
- Acceso a internet (para descargar modelos de Hugging Face la primera vez)

---

## Instalación

1. **Clona este repositorio o descarga el código fuente.**

2. **(Opcional) Crea un entorno virtual:**
    ```sh
    python -m venv .venv
    # Activa el entorno:
    # En Windows:
    .venv\Scripts\activate
    # En Linux/Mac:
    source .venv/bin/activate
    ```

3. **Instala las dependencias:**
    ```sh
    pip install -r requirements.txt
    ```
    Si no tienes `requirements.txt`, instala manualmente:
    ```sh
    pip install flask transformers torch pytesseract pillow python-docx pymupdf
    ```

4. **Instala Tesseract OCR:**
    - **Windows:** [Descarga aquí](https://github.com/tesseract-ocr/tesseract) y recuerda la ruta de instalación (ejemplo: `C:\Program Files\Tesseract-OCR\tesseract.exe`).
    - **Linux:**  
      ```sh
      sudo apt-get install tesseract-ocr
      ```
    - **Mac:**  
      ```sh
      brew install tesseract
      ```

5. **Configura la ruta de Tesseract en `app.py` si es necesario:**
    ```python
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ```

---

## Uso

1. Ejecuta la aplicación:
    ```sh
    python app.py
    ```

2. Abre tu navegador en [http://127.0.0.1:5000](http://127.0.0.1:5000)

3. Sube un archivo de texto, imagen, PDF o DOCX y haz clic en **Analizar Archivo**.

4. Verás:
    - Una lista de palabras ofensivas detectadas.
    - El texto con las palabras/frases ofensivas resaltadas.

---

## Notas

- El modelo por defecto es `unitary/toxic-bert`. Puedes cambiarlo por otro modelo de Hugging Face si lo deseas.
- Para producción, usa un servidor WSGI como Gunicorn o uWSGI.
- Si tienes problemas con dependencias, asegúrate de tener `pip` actualizado:
    ```sh
    pip install --upgrade pip
    ```

---

## Licencia

Este proyecto es solo para fines educativos y de investigación.

---