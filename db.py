import weaviate
import weaviate.classes as wvc
import torch
from sentence_transformers import SentenceTransformer

class PDFCollectionManager:
    def __init__(self):
        self.collection_name = "PDF_Documents"
        self.model_name = "BAAI/bge-m3"

        self.client = weaviate.connect_to_local()
       
        device = "cpu"
        if torch.cuda.is_available():
            device = "cuda"
        if torch.backends.mps.is_available():
            device = "mps"
        print(f"Using device: {device}")

        self.model = SentenceTransformer(self.model_name, device=device)

    def __del__(self):
        self.close()

    def create_collection(self):
        if self.client.collections.exists(self.collection_name):
            print("Collection already exists.")
            return
        self.client.collections.create(
            name=self.collection_name,
            properties=[
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="file", data_type=wvc.config.DataType.TEXT),
            ],
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),
        )
        print("Collection created.")

    def remove_collection(self):
        if not self.client.collections.exists(self.collection_name):
            print("Collection does not exist.")
            return
        self.client.collections.delete(self.collection_name)
        print("Collection removed.")

    def add_document(self, file_path: str, content: str):
        pdfdoc = self.client.collections.get(self.collection_name)
        vector = self.model.encode(content, convert_to_tensor=True).cpu().tolist()
        pdfdoc.data.insert({
            "content": content,
            "file": file_path,
        }, vector=vector)
        print(f"Document '{file_path}' added to collection.")

    def close(self):
        if self.client is None:
            return
        self.client.close()
        print("Client closed.")

if __name__ == "__main__":
    manager = PDFCollectionManager()
    manager.remove_collection()
    manager.create_collection()
    manager.close()
