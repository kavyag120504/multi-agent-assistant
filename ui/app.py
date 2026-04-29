# This file exists for legacy compatibility.
# The actual app lives in the project root: app.py
# Run from the project root with: streamlit run app.py

import sys
import os

# Add project root to path so imports work when run from ui/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Re-export everything from the root app
exec(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")).read())
