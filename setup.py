from setuptools import setup, find_packages
from codecs import open
setup(
    name='lightlog',
    version='0.1',
    description='log tool for multi-process or remote log server',
    long_description=str(open("README.md").read()),
    url='opconty - Overview',
    author='wangsong19',
    author_email='15507484608@163.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    py_modules=["lightlog"],
)
