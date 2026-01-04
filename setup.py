"""
Setup script for MICCHRIS Farms Inventory App
Windows build configuration
"""
from setuptools import setup, find_packages

setup(
    name="MICCHRIS_Inventory",
    version="1.0.0",
    description="Inventory Management System for MICCHRIS Farms",
    author="MICCHRIS Farms",
    packages=find_packages(),
    install_requires=[
        "customtkinter==5.2.2",
        "darkdetect==0.8.0",
        "reportlab==4.4.7",
        "Pillow>=10.0.0",  # For icon generation
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "micchris-inventory=main:main",
        ],
    },
)













