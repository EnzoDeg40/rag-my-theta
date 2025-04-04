import fitz  # PyMuPDF
import os

import db

def read_pdf_to_string(pdf_path):
    pdf_text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pdf_text += page.get_text()
    return pdf_text

def list_pdf_files_in_folder(folder_path):
    pdf_files = []
    if not os.path.exists(folder_path):
        return pdf_files
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, file_name))
    return pdf_files

if __name__ == "__main__":
    folder_path = "THETA_brochures"

    pdf_files = list_pdf_files_in_folder(folder_path)

    for pdf_file in pdf_files:
        print(f"Reading file: {pdf_file}")
        pdf_content = read_pdf_to_string(pdf_file)
        print(f"Content of {pdf_file}:\n{pdf_content}\n")

        collection_manager = db.PDFCollectionManager()
        collection_manager.add_document(
            file_path=pdf_file,
            title=os.path.basename(pdf_file),
            content=pdf_content
        )
        