from flask import Flask, request, send_file
from flask_cors import CORS
from get_data import extract_and_convert_to_json
from convert import convert_to_html
import os
import json
app = Flask(__name__)
CORS(app)  

with open('companies.json', 'w') as file:
    json.dump([], file)

@app.route('/query', methods=['POST'])
def handle_query():
    # Parse the JSON request
    data = request.json
    query = data.get('query', '')

    # Log or process the received query
    print(f"Received query: {query}")
    extract_and_convert_to_json(query)
    return '',204


@app.route('/convert', methods=['POST'])
def convert_to_pdf():
    data = request.get_json()
    markdown_content = data.get('content', '')
    print(f"Received markdown content: {markdown_content}")
    markdown_content = str(markdown_content)
    convert_to_html(markdown_content)
    if not os.path.exists("pathway.html"):
        return {"error": "Failed to generate PDF"}, 500

    return {"message": "PDF generated successfully"}

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    output_file = 'pathway.html'

    # Check if the PDF exists
    if not os.path.exists(output_file):
        return {"error": "PDF not found"}, 404

    return send_file(output_file, as_attachment=True, download_name='pathway.html', mimetype='text/html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Run Flask server on port 5001