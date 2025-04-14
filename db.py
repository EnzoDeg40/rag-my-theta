import weaviate
import weaviate.classes as wvc
import torch
from sentence_transformers import SentenceTransformer
import re

class PDFCollectionManager:
    def __init__(self, prefix_collection_name: str = "PDF_Documents", model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name
        sanitized_model_name = re.sub(r'[^a-zA-Z0-9]', '_', self.model_name)
        self.collection_name = f"{prefix_collection_name}_{sanitized_model_name}"
        print(f"Collection name: {self.collection_name}")

        self.client = weaviate.connect_to_local()
       
        self.device = "cpu"
        if torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        print(f"Using device for {__class__.__name__}: {self.device}")

        self.model = SentenceTransformer(self.model_name, device=self.device)

    def create_collection(self):
        if self.client.collections.exists(self.collection_name):
            print(f"Collection '{self.collection_name}' already exists.")
            return
        self.client.collections.create(
            name=self.collection_name,
            properties=[
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="file", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="chunk", data_type=wvc.config.DataType.NUMBER),
                wvc.config.Property(name="type", data_type=wvc.config.DataType.TEXT),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
        )
        print(f"Collection '{self.collection_name}' created.")

    def remove_collection(self):
        if not self.client.collections.exists(self.collection_name):
            print("Collection does not exist.")
            return
        self.client.collections.delete(self.collection_name)
        print(f"Collection '{self.collection_name}' removed.")
   
    def add_document(self, file_path: str, content: str):
        pdfdoc = self.client.collections.get(self.collection_name)

        if self.is_document_in_collection(file_path, pdfdoc):
            print(f"Document '{file_path}' already exists in the collection.")
            return
        
        vector = self.model.encode(content, convert_to_tensor=True).to(self.device).tolist()
        pdfdoc.data.insert({
            "content": content,
            "file": file_path,
            "chunk": 0
        }, vector=vector)
        print(f"Document '{file_path}' added to collection.")

    def add_document_chunked(self, file_path: str, content: str, chunk: list[str]):
        pdfdoc = self.client.collections.get(self.collection_name)

        if self.is_document_in_collection(file_path, pdfdoc):
            print(f"Document '{file_path}' already exists in the collection.")
            return

        for i, chunk_text in enumerate(chunk):
            vector = self.model.encode(chunk_text, convert_to_tensor=True).to(self.device).tolist()
            pdfdoc.data.insert({
                "content": chunk_text,
                "file": file_path,
                "chunk": i,
                "type": "text"
            }, vector=vector)

    def search(self, query: str, limit: int = 10):
        pdfdoc = self.client.collections.get(self.collection_name)
        vector = self.model.encode(query, convert_to_tensor=True).to(self.device).tolist()

        results = pdfdoc.query.near_vector(
            near_vector=vector,
            limit=limit,
            return_metadata=["distance"],  # or 'certainty'
            return_properties=True
        )

        results_list = []

        for obj in results.objects:
            results_list.append({
                "content": obj.properties["content"],
                "file": obj.properties["file"],
                "chunk": obj.properties["chunk"],
                "distance": obj.metadata.distance
            })
        
        return results_list

    def print_search_results(self, results):
        for result in results:
            print(result)

    def close(self):
        self.client.close()
        print("Client closed.")

    def is_document_in_collection(self, file_path: str, collection):
        results = collection.query.fetch_objects(
            filters=wvc.query.Filter.by_property("file").equal(file_path)
        )
        return len(results.objects) > 0

if __name__ == "__main__":
    manager = PDFCollectionManager()
    manager.remove_collection()
    manager.create_collection()
    manager.close()
