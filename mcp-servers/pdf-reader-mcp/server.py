from mcp.server.fastmcp import FastMCP
import PyPDF2
import io
import base64

mcp = FastMCP("PDF Reader Server")

@mcp.tool()
def read_pdf(base64_pdf: str) -> str:
    """Extract text from a PDF file provided as a base64 string.
    
    Args:
        base64_pdf: The PDF file contents encoded as a base64 string.
    """
    try:
        pdf_bytes = base64.b64decode(base64_pdf)
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = []
        for i, page in enumerate(reader.pages):
            text_content.append(f"--- Page {i+1} ---")
            text_content.append(page.extract_text() or "")
            
        return "\n".join(text_content)
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
