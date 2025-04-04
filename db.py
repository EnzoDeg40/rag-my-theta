import weaviate
import weaviate.classes as wvc

client = weaviate.connect_to_local()

def create_collection():
    if client.collections.exists("PDF_Documents"):
        return
    client.collections.create(
        name="PDF_Documents",
        properties=[
            wvc.config.Property(name="title", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
            wvc.config.Property(name="file", data_type=wvc.config.DataType.TEXT),
        ],
    )

def remove_collection():
    if not client.collections.exists("PDF_Documents"):
        return
    client.collections.delete("PDF_Documents")

if __name__ == "__main__":
    remove_collection()
    create_collection()
    client.close()


