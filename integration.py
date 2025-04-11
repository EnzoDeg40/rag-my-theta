import fitz  # PyMuPDF
import os
import db
import textchunk

class PDFImporter:
    def __init__(self, folder_path="data"):
        self.folder_path = folder_path
        self.collection_manager = db.PDFCollectionManager()

    def read_pdf_to_string(self, pdf_path):
        pdf_text = ""
        try:
            with fitz.open(pdf_path) as pdf_document:
                for page in pdf_document:
                    pdf_text += page.get_text()
        except Exception as e:
            print(f"An error occurred while reading the PDF: {e}")
        if not pdf_text:
            print(f"PDF file '{pdf_path}' is empty or could not be read.")
        return pdf_text

    def list_pdf_files_in_folder(self):
        if not os.path.exists(self.folder_path):
            return []
        return [
            os.path.join(self.folder_path, f)
            for f in os.listdir(self.folder_path)
            if f.lower().endswith('.pdf')
        ]

    def import_pdfs(self):
        self.collection_manager.create_collection()
        pdf_files = self.list_pdf_files_in_folder()

        for pdf_file in pdf_files:
            # TODO: make the is_document_in_collection function more portable
            collection = self.collection_manager.client.collections.get(self.collection_manager.collection_name)
            if self.collection_manager.is_document_in_collection(pdf_file, collection):
                print(f"Document '{pdf_file}' already exists in the collection.")
                continue

            pdf_content = self.read_pdf_to_string(pdf_file)
            textchunker = textchunk.TextChunker(max_tokens=150)
            textlist = textchunker.chunk(pdf_content)

            for i, chunk in enumerate(textlist):
                print(f"Chunk {i+1} ({textchunker.count_tokens(chunk)} tokens) :\n{chunk}\n\n\n")

            self.collection_manager.add_document_chunked(
                file_path=pdf_file,
                content=pdf_content,
                chunk=textlist
            )

        self.collection_manager.close()
        print("All documents added to the collection.")

if __name__ == "__main__":
    importer = PDFImporter(folder_path="data")
    importer.import_pdfs()
