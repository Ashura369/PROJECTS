import PyPDF2

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        with open('extracted_pdf_text.txt', 'w', encoding='utf-8') as out_file:
            out_file.write(text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    read_pdf('1 Project Guidelines.pdf')
