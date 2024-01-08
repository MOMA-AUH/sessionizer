from setuptools import find_packages, setup

setup(
    name="sessionizer",
    version="0.1.3",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["sessionizer = sessionizer.main:run"]},
    python_requires=">=3.10",
    author="Simon Opstrup Drue",
    author_email="simondrue@gmail.com",
)
