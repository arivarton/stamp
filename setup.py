# Packaging references:
# https://github.com/pypa/packaging/
# https://packaging.pypa.io/en/latest/
# https://setuptools.readthedocs.io/en/latest/setuptools.html

from os import path
from setuptools import setup, find_packages

exec_dir = path.abspath(path.dirname(__file__))

with open(path.join(exec_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stamp',
    version='0.0.8',
    description='Register workhours in terminal.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/arivarton/stamp/',
    author='arivarton',
    author_email='packager@arivarton.com',
    license='GNU GPL v3',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Other Audience',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: POSIX :: Linux',
    ],
    keywords='work hours time log register stamp',
    python_requires='>=3',
    install_requires=[
        'sqlalchemy',
        'reportlab',
    ],
    packages=find_packages(exclude=['tests', ]),
    entry_points={
        'console_scripts': [
            'stamp = stamp.stamp:main',
        ]
    }
)
