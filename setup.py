from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as fr:
    requirements = fr.read().splitlines()

setup(
    name='tcd',
    version='0.0.1',
    packages=find_packages(),
    package_dir={
        'tcd': 'tcd',
    },
    license='MIT License',
    url='https://github.com/ViZiD/tcd',
    entry_points={
        'console_scripts': [
            'tcd = tcd.app.run:main',
        ],
    },
    install_requires=requirements,
    author='radik islamov',
    author_email='vizid1337@gmail.com',
    long_description=long_description,
    description='TCD is tool for decrypted Telegram Desktop media cache',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Security',

    ],
    python_requires='>=3.9'
)
