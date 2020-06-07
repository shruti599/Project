import io
from flask import url_for
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import docx2txt

def extract_text_from_pdf(pdf_path):
    # path = 'static/uploaded_files/Stress_Management.pdf'
    try:
        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle)
        page_interpreter = PDFPageInterpreter(resource_manager, converter)
        
        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
        
        # close open handles
        converter.close()
        fake_file_handle.close()
        
        if text:
            return text
        else:
            return ""
    except:
        return None

      
# print(extract_text_from_pdf('static\\uploaded_files\\Unit_2.pdf'))

def extract_text(text_path):
    text = docx2txt.process(text_path)
    return text

# print(extract_text('static\\uploaded_files\\The_12_Principles_of_Animation.docx'))

def get_image_name(img):
    image = img.replace('url("','').replace('")','').strip()
    image = image[36:48]
    image = image.strip()
    return image

def get_image_path(img):
    path = "/static/images/"+img+".jpg"
    return path