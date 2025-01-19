"""Python setup.py for amexsheets package"""
from setuptools import find_packages, setup

from utils import read, read_requirements

setup(
    name="amexsheets",
    version=read("amexsheets", "VERSION"),
    description="Track Amex expenses on google sheets created by anthonyprinaldi",
    url="https://github.com/anthonyprinaldi/AmexSheets/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="anthonyprinaldi",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
)