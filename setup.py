from pathlib import Path

from setuptools import find_packages
from setuptools import setup


BASE_DIR = Path(__file__).parent

README = (
    BASE_DIR / "README.md"
).read_text(encoding="utf-8")


setup(
    name="grc-asset-register",
    version="1.0.0",
    description=(
        "GRC Information Asset Register "
        "with automated validation and CIA scoring"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author="Daniel Mogilevskiy",
    license="MIT",
    python_requires=">=3.8",

    package_dir={
        "": "src",
    },

    packages=find_packages(
        where="src"
    ),

    entry_points={
        "console_scripts": [
            "asset-register=asset_register.cli:main",
        ],
    },

    include_package_data=True,
)