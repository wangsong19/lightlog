from setuptools import setup
from os import system

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="lightlog",
    version="0.1",
    description="tool of log for multi-process/remote record",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="wangsong19",
    author_email="15507484608@163.com",

    packages=["lightlog"],
    package_dir={"lightlog": "lightlog"},
    include_package_data=True,
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    zip_safe=False
)
system("rm -r build dist lightlog.egg-info")
