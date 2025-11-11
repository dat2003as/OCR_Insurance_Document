import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from src import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
