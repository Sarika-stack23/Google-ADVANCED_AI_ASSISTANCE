import os
import sys
import base64
from mcp.server.fastmcp import FastMCP

# Ensure the backend module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.src.services.gemini_service import GeminiVisionService

mcp = FastMCP("Image Solver Server")

@mcp.tool()
def extract_and_solve_image(base64_image: str, mime_type: str = "image/jpeg") -> dict:
    """Extract math problems from an image and solve them using Gemini Vision.
    
    Args:
        base64_image: The image file contents encoded as a base64 string.
        mime_type: The mime type of the image (default 'image/jpeg').
    """
    try:
        image_bytes = base64.b64decode(base64_image)
        service = GeminiVisionService()
        result = service.extract_and_solve(image_bytes, mime_type)
        return result
    except Exception as e:
        return {"error": f"Error solving image: {str(e)}"}

if __name__ == "__main__":
    mcp.run(transport='stdio')
