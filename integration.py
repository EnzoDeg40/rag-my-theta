import fitz  # PyMuPDF
import os
import db

class PDFImporter:
    def __init__(self, folder_path="data"):
        self.folder_path = folder_path
        self.collection_manager = db.PDFCollectionManager()

    def read_pdf_to_string(self, pdf_path):
        pdf_text = ""
        with fitz.open(pdf_path) as pdf_document:
            for page in pdf_document:
                pdf_text += page.get_text()
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
            pdf_content = self.read_pdf_to_string(pdf_file)
            self.collection_manager.add_document(
                file_path=pdf_file,
                content=pdf_content
            )

        self.collection_manager.close()
        print("All documents added to the collection.")

if __name__ == "__main__":
    importer = PDFImporter(folder_path="data")
    importer.import_pdfs()
