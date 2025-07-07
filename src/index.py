# import modules for server
from dotenv import load_dotenv
load_dotenv()

import subprocess
from flask import Flask, jsonify, request


from graph.RetrieveLLamaIndex import RetrieverLlamaIndex
from graph.DocumentToGraph import DocumentToGraph


app = Flask(__name__)

@app.route('/upload-document', methods=['POST'])
def upload_document():
	try:
		#print("received request")
		data = request.json
		document_id = data["document_id"]

		#print(data)
		#print(message)
		result = DocumentToGraph().run(document_id)
		#print("Server Result")
		#print(result)
		return jsonify({'response': result}), 200
	except Exception as e:
		print(e)
		return "Error",400

@app.route('/query-document', methods=['POST'])
def query_document():
	try:
		#print("received request")
		data = request.json
		#print(data)
		document_id = data["document_id"]
		index_name = "entity"
		#print(message)
		query = data["query"]
		result = RetrieverLlamaIndex(index_name).retrieve(document_id,query)
		#print("Server Result")
		#print(result)
		return jsonify({'response': result}), 200
	except Exception as e:
		print(e)
		return "Error",400

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=4404)
