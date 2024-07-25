from setuptools import find_packages, setup

setup(
    name="sessionizer",
    version="0.2.3",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["sessionizer = sessionizer.main:app"]},
    test_suite="tests",
    package_data={"": ["tests/*"]},
    python_requires=">=3.10",
    install_requires=["typer", "rich"],
    author="Simon Opstrup Drue",
    author_email="simondrue@gmail.com",
)
