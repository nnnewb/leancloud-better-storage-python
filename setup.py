import setuptools
from setuptools import find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

packages = find_packages(exclude=('tests',))

setuptools.setup(
    name="leancloud-better-storage",
    version="0.1.7",
    author="weak_ptr",
    author_email="weak_ptr@outlook.com",
    description="Better ORM wrapper of leancloud storage python sdk.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nnnewb/leancloud-better-storage-python",
    packages=packages,
    install_requires=['leancloud==2.1.8', ],
    license='LGPL',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
)
