import weaviate
import weaviate.classes as wvc

class PDFCollectionManager:
    def __init__(self):
        self.client = weaviate.connect_to_local()
        self.collection_name = "PDF_Documents"

    def create_collection(self):
        if self.client.collections.exists(self.collection_name):
            print("Collection already exists.")
            return
        self.client.collections.create(
            name=self.collection_name,
            properties=[
                wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="file", data_type=wvc.config.DataType.TEXT),
            ],
        )
        print("Collection created.")

    def remove_collection(self):
        if not self.client.collections.exists(self.collection_name):
            print("Collection does not exist.")
            return
        self.client.collections.delete(self.collection_name)
        print("Collection removed.")

    def add_document(self, file_path: str, title: str, content: str):
        pdfdoc = self.client.collections.get(self.collection_name)
        pdfdoc.data.insert({
            "title": title,
            "content": content,
            "file": file_path,
        })
        print(f"Document '{title}' added to collection.")


if __name__ == "__main__":
    manager = PDFCollectionManager()
    manager.remove_collection()
    manager.create_collection()

