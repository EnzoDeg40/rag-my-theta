import fitz  # PyMuPDF
import os
import io
import db
import textchunk
import vision
from PIL import Image


class PDFImporter:
    def __init__(self, folder_path="data"):
        self.folder_path = folder_path
        self.collection_manager = db.PDFCollectionManager()
        self.vision = vision.ImageDescriber()

    def pixmap_to_pil(self, pixmap):
        return Image.open(io.BytesIO(pixmap.tobytes("png")))

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
        pdf_text = " ".join(pdf_text.split())
        return pdf_text
    
    def read_pdf_to_images(self, pdf_path: str) -> list:
        pdf_images = []
        try:
            with fitz.open(pdf_path) as pdf_document:
                for page_number in range(min(3, len(pdf_document))):
                    page = pdf_document[page_number]
                    pdf_images.append(page.get_pixmap())
        except Exception as e:
            print(f"An error occurred while reading the PDF: {e}")
        if not pdf_images:
            print(f"PDF file '{pdf_path}' is empty or could not be read.")
        return pdf_images

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
        
            pdf_images = []
            pixmaps = self.read_pdf_to_images(pdf_file)
            for pixmap in pixmaps:
                pil_image = self.pixmap_to_pil(pixmap)
                caption = self.vision.describe_image(pil_image)
                pdf_images.append(caption)

            textchunker = textchunk.TextChunker(max_tokens=150)
            textlist = textchunker.chunk(pdf_content)

            self.collection_manager.add_document_chunked(
                file_path=pdf_file,
                chunk_text=textlist,
                images=pdf_images,
            )

            print(f"Document '{pdf_file}' added to collection with {len(textlist)} chunks text and {len(pdf_images)} images.")

        self.collection_manager.close()
        print("All documents added to the collection.")

if __name__ == "__main__":
    importer = PDFImporter(folder_path="data")
    importer.import_pdfs()
