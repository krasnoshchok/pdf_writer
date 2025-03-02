from flask import Flask, render_template, request, send_file
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "pdf_file" not in request.files:
        return "No file uploaded", 400

    file = request.files["pdf_file"]
    if file.filename == "":
        return "No selected file", 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    return {"filename": filename}, 200


@app.route("/generate", methods=["POST"])
def generate_pdf():
    data = request.json
    filename = data.get("filename")
    coordinates = data.get("coordinates")

    if not filename or not coordinates:
        return "Invalid data", 400

    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    output_path = os.path.join(app.config["OUTPUT_FOLDER"], f"output_{filename}")

    doc = fitz.open(input_path)
    page = doc[0]  # Modify first page only

    for coord in coordinates:
        x, y = coord["coords"]
        value = coord["value"]

        text = fitz.Point(x, y)
        page.insert_text(text, value, fontsize=12, color=(0, 0, 0))

    doc.save(output_path)
    return {"output_file": f"output_{filename}"}, 200


@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
