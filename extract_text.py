from pypdf import PdfReader
import os

def main():
    pdf_files = os.listdir('pdfs/')
    for file in pdf_files:
        reader = PdfReader('pdfs/'+file)
        # printing number of pages in pdf file
        print(len(reader.pages))
        with open ('textfiles/' +file[:5]+ '.txt', 'w') as f:
            for i in range(0,len(reader.pages)):
                page = reader.pages[i]
                text = page.extract_text()
                f.write(text)
if __name__ == "__main__":
    main()





