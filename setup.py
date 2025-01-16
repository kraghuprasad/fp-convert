from setuptools import find_packages, setup

setup(
    name="fp-convert",
    version="0.1.0",
    description="Convert Freeplane mindmaps to print-quality PDF documents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="K Raghu Prasad",
    author_email="raghuprasad@duck.com",
    url="https://github.com/kraghuprasad/fp-convert",
    packages=find_packages(exclude=["tests*"]),
    package_data={
        "fp_convert": ["resources/*"],
    },
    include_package_data=True,
    install_requires=[
        "freeplane-io",
        "pylatex",
        "pathlib",
        "cairosvg",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers, Users",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="freeplane mindmap pdf conversion latex specs spefication specifications documentation",
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "fp-convert=fp_convert.__main__:main",  # Assuming you have a main function in __init__.py
        ],
    },
    extras_require={
        "dev": ["pytest", "sphinx"],
    },
    license="Apache License 2.0",
)
