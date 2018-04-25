from setuptools import setup, find_packages

setup(
    name='PubMed Best Match',
    version='0.1',
    packages=find_packages(),
    install_requires=[
          'requests', 'docopt', 'regex'
      ],
    entry_points={
        'console_scripts': [
            'pbm = pbm:main'
        ]
    },
    python_requires=">=3.4",
    author="Nicolas Fiorini",
    author_email="nicolas.fiorini@nih.gov",
    description="This is an Example Package",
    url="https://github.com/ncbi-nlp/PubMed-Best-Match/",
)
