import setuptools

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="mbench",
    packages=['mbench'],
    install_requires=install_requires,
    version="0.0.5"
)