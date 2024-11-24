from crewai_tools import BaseTool
import fitz  # PyMuPDF

class CustomPDFReadTool(BaseTool):
    name: str = "PDF Read Tool"
    description: str = "A tool extracting text from PDF files."

    def _run(self, file_path: str) -> str:
        try:
            # Open the PDF file
            document = fitz.open(file_path)
            text = ""
            # Extract text from each page
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                text += page.get_text()
            return text
        except Exception as e:
            return f"An error occurred: {str(e)}"