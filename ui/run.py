#!/usr/bin/env python3
"""
Entry point for the Document Processing Hub UI.
Run this script to start the Streamlit application.
"""

import streamlit as st
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from app import main

if __name__ == "__main__":
    main()
