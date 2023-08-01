from setuptools import setup
from typing import List, AnyStr

def deps_public() -> List[AnyStr]:
    """
    Dependency fetched

    :return: dependencies ar list of strings
    """
    with open("requirements.txt", "rt") as handle:
        req = handle.readlines()
    return req


setup(
    name="cw-backend",
    zip_safe=False,
    python_requires=">=3.10",
    package_dir={"cw_backend": "./src/cw_backend"},
    classifiers=[
        "Private :: Do Not Upload",
    ],
    install_requires=deps_public(),
)
