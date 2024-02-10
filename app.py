from flask import Flask, render_template, request, send_from_directory
from azure.cosmos import CosmosClient, PartitionKey
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Konfiguracja Azure Cosmos DB
url = 'https://zadanie7.documents.azure.com:443/'
key = 'Ljt5QNPkZmAr2opfycxBLyfypj5OKTtVGDoN6jOGCV270cu4ov0PHNapptl1Piapx56vNGd1rPokACDbmKJBeQ=='
client = CosmosClient(url, credential=key)
database_name = 'zadanie7'
container_name = 'Uploads'
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Zapisz plik na dysku
    filename = str(uuid.uuid4()) + '_' + file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # Dodaj metadane do bazy danych
    metadata = {
        'id': str(uuid.uuid4()),
        'filename': filename,
        'filetype': file.content_type,
        'upload_date': datetime.utcnow().isoformat()
    }
    container.create_item(body=metadata)

    return 'File uploaded successfully'


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
