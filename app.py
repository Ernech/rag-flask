from flask import Flask, jsonify,request
from flask_cors import CORS
from waitress import serve
from flask_swagger_ui import get_swaggerui_blueprint
from dotenv import load_dotenv
from typing import List
load_dotenv() # take environment variables from .env.
from services.process_doc import index_pdf,is_base64_pdf, is_pdf_filename, save_base64_pdf,check_if_doc_exists, db_global as _
from services.read_docs import get_results
import os
import logging
from database.data_access.indexed_document_data_access import IndexedDocumentDataAccess
    # Now you can access them using os.getenv()
MANUALES_PATH = os.getenv("MANUALES_PATH")

app = Flask(__name__)#multi-qa-MiniLM-L6-cos-v1 #intfloat/multilingual-e5-large
CORS(app=app)
#app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Recommended to set to False
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.json'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)
app.register_blueprint(swaggerui_blueprint)


@app.route('/update/vectorial-db',methods=["POST"])
def update_vectorial_db():
    try:
        for filename in os.listdir(MANUALES_PATH):
            if filename.endswith(".pdf"):
                path = os.path.join(MANUALES_PATH, filename)
                index_pdf(path)
        return jsonify({"Codigo":100, "Restuesta":True, "Mensaje":"Se ha actualizado la base de datos vectorial"}), 201
    except Exception as e: 
        return jsonify({"Codigo":400, "Restuesta":False, "Mensaje":f"Ocrurrió un error {e}"}),500
    

@app.route("/load/document", methods=["POST"])
def load_documento_to_vectorial_db():
    try:
        req_data = request.get_json()
        if req_data:
            archivo:str = req_data.get("Archivo")
            nombre_archivo:str = req_data.get("NombreArchivo")
            if not archivo:
                return jsonify({"Codigo":300, "Respuesta":True, "Mensaje":f"El campo archivo está vacío o no es válido"}),400
            if not nombre_archivo:
                return jsonify({"Codigo":300, "Respuesta":True, "Mensaje":f"El campo nobre archivo está vacío o no es válido"}),400
            #Verificar si el base 64 es un pdf
            if not is_base64_pdf(archivo):
                return jsonify({"Codigo":300, "Respuesta":True, "Mensaje":f"El archivo no es un documento PDF válido"}),400
            #Verificar si el nombre del archivo es un pfd
            if not is_pdf_filename(nombre_archivo):
                return jsonify({"Codigo":300, "Respuesta":True, "Mensaje":f"El nombre de archivo no corresponde a documento PDF válido"}),400
            #Verificar si el documento ya existe en el file system
            full_path = os.path.join(MANUALES_PATH, nombre_archivo)
            if check_if_doc_exists(archivo):
                return jsonify({"Codigo":300, "Respuesta":True, "Mensaje":f"El archivo '{nombre_archivo}' ya existe el directorio '{MANUALES_PATH}'"}),400
            #Guardar documento pdf
            save_base64_pdf(archivo,MANUALES_PATH,nombre_archivo)
            #Actualizar la base de conocimiento
            index_pdf(full_path)
      
            return jsonify({"Codigo":100, "Respuesta":True, "Mensaje":f"Se ha registrado el documento"}),201
        else:
            return jsonify({"Codigo":300, "Respuesta":True, "Mensaje":f"No se recibió data válida"}),400
    except Exception as e: 
        return jsonify({"Codigo":400, "Respuesta":False, "Mensaje":f"Ocrurrió un error {e}"}),500


@app.route('/rag/query', methods=['POST'])
def rag_query():
    try:
         req_data = request.get_json()
         if req_data:
            query:str = req_data.get("query")
            sources:List[str] = req_data.get("sources")
            if not query:
                return jsonify({"Codigo":300, "Respuesta":False, "Fragmentos":[], "Mensaje":f"El query no puede estar vacío"}),400
            if not sources:
                return jsonify({"Codigo":300, "Respuesta":False,"Fragmentos":[], "Mensaje":f"La fuentes no pueden estar vacías"}),400
            results = get_results(query=query,sources=sources)
            if not results:
                return jsonify({"Codigo":300, "Respuesta":False, "Fragmentos":[],"Mensaje":f"No se encontraron resultados en las fuentes: {sources}"}),400
            fragments = [ {"documento":doc.page_content,"source":doc.metadata.get("source")} for (doc, _) in results ]
            return jsonify({"Codigo":100, "Respuesta":True, "Fragmentos":fragments, "Mensaje":f"Se ha recuperado la información"}),200

    except Exception as e:
        print(e)
        return jsonify({"Codigo":400, "Respuesta":False, "Mensaje":f"Ocrurrió un error {e}"}),500

@app.route('/rag/indexed_documents',methods=["GET"])
def get_all_indexed_documents():
    try:
        indexed_documents_da = IndexedDocumentDataAccess()
        retrieved_indexed_documents_list = indexed_documents_da.getAllIndexedDocuments()
        if len(retrieved_indexed_documents_list) >0:
            retrieved_indexed_documents_json = [ {
                "document_id": document.document_id, 
                "file_name": document.file_name, 
                "file_hash": document.file_hash, 
                "file_path": document.file_path, 
                "file_source": document.file_source, 
                "indexed_at": document.indexed_at, 
                "indexed_by": document.indexed_by, 
                "status": document.status, 
                "embedding_model": document.embedding_model, 
                "chunk_count": document.chunk_count
            }  for document in retrieved_indexed_documents_list]
            return jsonify({"Codigo":100, "Respuesta":True, "Mensaje":f"Documentos recuperados","IndexedDocuments":retrieved_indexed_documents_json}),200   
        else:
            return jsonify({"Codigo":400, "Respuesta":False, "Mensaje":f"No se encontraron documentos indexados","IndexedDocuments":[]}),404   
    except Exception as e:
          return jsonify({"Codigo":400, "Respuesta":False, "Mensaje":f"Ocrurrió un error {e}","IndexedDocuments":[]}),500    


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if os.getenv("FLASK_ENV") == "local-development":
        logging.info("App runing on local dev mode")
        app.run(debug=True)
    else:
        logging.info("App runing on serve mode")
        serve(app, host="0.0.0.0", port=8000)
