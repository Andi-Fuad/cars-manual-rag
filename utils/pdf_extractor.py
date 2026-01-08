import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List
from PIL import Image
import io

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
    
    def extract_text_by_page(self) -> Dict[int, str]:
        """Extract text from each page."""
        text_by_page = {}
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            text_by_page[page_num] = text
        return text_by_page
    
    def extract_images_by_page(self, output_dir: str = "extracted_images") -> Dict[int, List[str]]:
        """Extract images from each page and save them."""
        Path(output_dir).mkdir(exist_ok=True)
        images_by_page = {}
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            image_list = page.get_images()
            page_images = []
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save image
                image_filename = f"page_{page_num}_img_{img_index}.{image_ext}"
                image_path = Path(output_dir) / image_filename
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                page_images.append(str(image_path))
            
            images_by_page[page_num] = page_images
        
        return images_by_page
    
    def get_document_metadata(self) -> Dict:
        """Get PDF metadata."""
        return {
            "num_pages": len(self.doc),
            "metadata": self.doc.metadata
        }
    
    def close(self):
        """Close the PDF document."""
        self.doc.close()