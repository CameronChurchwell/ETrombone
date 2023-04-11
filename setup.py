from setuptools import setup


with open('README.md') as file:
    long_description = file.read()

setup(
    name='etrombone',
    description='Electronic Trombone',
    version='0.0.1',
    author='Cameron Churchwell',
    author_email='cameronchurchwell2024@u.northwestern.edu',
    url='https://github.com/cameronchurchwell/etrombone',
    install_requires=[
        'pedalboard',
        'pyopenxr'
    ],
    packages=['etrombone'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPL')
