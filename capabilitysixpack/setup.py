import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='capabilitysixpack',
    version='0.0.1',
    author='Evan Schock',
    author_email='eschock13@gmail.com',
    description='Capability Sixpack',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/eschock13/capabilityplots',
    packages=['capabilityplots'],
    install_requires=['matplotlib', 'statistics', 'probscale', 'scipy', 'numpy',
                    'tkinter', 'time', 'pandas', 'selenium', 'os', 'datetime',
                    'glob', 'pathlib', 'csv']
)
