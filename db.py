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
       
        self.device = self._get_device()
        print(f"Using device for {__class__.__name__}: {self.device}")

        self.model = SentenceTransformer(self.model_name, device=self.device)

    def _get_device(self):
        if torch.backends.mps.is_available():
            return torch.device("mps")
        elif torch.cuda.is_available():
            return torch.device("cuda")
        else:
            return torch.device("cpu")

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
   
    def add_document_chunked(self, file_path: str, chunk_text: list[str], images: list = None):
        pdfdoc = self.client.collections.get(self.collection_name)

        if self.is_document_in_collection(file_path, pdfdoc):
            print(f"Document '{file_path}' already exists in the collection.")
            return

        for i, chunk_text in enumerate(chunk_text):
            vector = self.model.encode(chunk_text, convert_to_tensor=True).to(self.device).tolist()
            pdfdoc.data.insert({
                "content": chunk_text,
                "file": file_path,
                "chunk": i,
                "type": "text"
            }, vector=vector)
    
        if images:
            for i, image in enumerate(images):
                vector = self.model.encode(image, convert_to_tensor=True).to(self.device).tolist()
                pdfdoc.data.insert({
                    "content": image,
                    "file": file_path,
                    "chunk": i,
                    "type": "image"
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
    
    def search_in_file(self, file_path: str, query: str, limit: int = 10):
        pdfdoc = self.client.collections.get(self.collection_name)
        vector = self.model.encode(query, convert_to_tensor=True).to(self.device).tolist()

        results = pdfdoc.query.near_vector(
            near_vector=vector,
            filters=wvc.query.Filter.by_property("file").equal(file_path),
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
    # manager.remove_collection()
    # manager.create_collection()
    
    search_results = manager.search_in_file("BLM.pdf", "Quels sont les transports disponibles ?", limit=3)
    print("Search results:")
    manager.print_search_results(search_results)
    
    manager.close()
