"""
Run the Farmer Crop Recommendation Website

This script starts the FastAPI server with the web interface.
"""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    print("=" * 70)
    print("🌾 FARMER CROP RECOMMENDATION SYSTEM")
    print("=" * 70)
    print("\nStarting web server...")
    print("\n📍 Access the website at: http://localhost:8000")
    print("📍 API documentation at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 70)
    
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
