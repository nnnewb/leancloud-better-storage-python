import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="better-leancloud-storage",
    version="0.0.1",
    author="weak_ptr",
    author_email="weak_ptr@outlook.com",
    description="better ORM wrapper of leancloud storage python sdk.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nnnewb/better-leancloud-storage-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: LGPLv3 License",
        "Operating System :: OS Independent",
    ],
)
