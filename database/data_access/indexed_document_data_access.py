from database.db_connection import get_connection
from database.models.indexed_document_model import IndexedDocumentModel
import psycopg2
class IndexedDocumentDataAccess:

    def __init__(self):
        self.conn=get_connection()

    def getAllIndexedDocuments(self):
        indexed_documents:list[IndexedDocumentModel]=[]
        query = """
        SELECT document_id, 
                file_name, 
                file_hash, 
                file_path, 
                file_source, 
                indexed_at, 
                indexed_by, 
                status, 
                embedding_model, 
                chunk_count
                FROM public.indexed_documents;
        """
        with self.conn.cursor() as cur:
            try:
                cur.execute(query=query)
                data = cur.fetchall()
                for indexed_document in data:
                    try:
                        indexed_document_retrieved = IndexedDocumentModel.from_db_row(indexed_document)                     
                        indexed_documents.append(indexed_document_retrieved)                      
                    except Exception as e:
                        raise Exception("⚠️ Error procesando fila:", e)
               
            except psycopg2.ProgrammingError as e:
                raise psycopg2.ProgrammingError(f"Programming Error at getting all indexed documents: {e}")
            except psycopg2.OperationalError as e:
                raise psycopg2.OperationalError(f"Operational Error at getting all indexed documents: {e}")
            except psycopg2.Error as e:
                raise psycopg2.Error(f"Database Error at getting all indexed documents: {e}")
            finally:
                if 'conn' in locals() and self.conn:
                    self.conn.close()
                return indexed_documents   

           