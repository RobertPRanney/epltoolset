import setuptools

def readme():
    with open("README.md", "r") as in_file:
        return in_file.read()

setuptools.setup(
    name="epltoolset",
    version="0.2.10",
    description="Simplify Oracle ETL scripts",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url='http://github.com.robertpranney/epltoolset',
    author='Robert Ranney',
    author_email='robertpranney@gmail.com',
    packages=['epltoolset'],
    include_package_data=True,
    python_requires='>=3.6',
    test_suite='nose.collector',
    tests_require=['nose'],
    install_requires=[
        'markdown',
        'cx_Oracle',
        'pandas'
    ],
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Database :: Front-Ends"
    ),
    scripts=['bin/manage-oracle-creds'],
)
