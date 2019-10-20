from setuptools import setup

setup(name='radiology',
      version='0.1',
      description='Experiments and code for processing radiology reports',
      url='http://github.com/dhruvrajan/radiology-nlp',
      author='Dhruv Rajan',
      author_email='dhruv@cs.utexas.edu',
      license='MIT',
      packages=['radiology'],
      scripts=['bin/get_dell_data.py'],
      zip_safe=False, install_requires=['allennlp', 'nltk'])
