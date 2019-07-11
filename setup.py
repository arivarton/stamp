# Packaging references:
# https://github.com/pypa/packaging/
# https://packaging.pypa.io/en/latest/
# https://setuptools.readthedocs.io/en/latest/setuptools.html

from os import path, makedirs, system
from glob import glob
from distutils.command.build_py import build_py as _build_py
from setuptools import setup, find_packages
from stamp.constants import SYSTEM_LOCALE_DIR, VERSION


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', encoding='utf-8') as f:
    install_requires = f.read().rstrip().split('\n')


class build_py(_build_py):
    """Custom distutils command to build translations."""
    def __init__(self, *args, **kwargs):
        _build_py.__init__(self, *args, **kwargs)
        # Keep list of files to appease bdist_rpm.  We have to keep track of
        # all the installed files for no particular reason.
        self.mofiles = []

    def run(self):
        """Compile translation files (requires gettext)."""
        _build_py.run(self)
        msgfmt = 'msgfmt'
        status = system(msgfmt + ' -V')
        if status == 0:
            for pofile in sorted(glob('locale/*.po')):
                lang = path.basename(pofile).split('.')[0]
                dirname = path.join(SYSTEM_LOCALE_DIR, '{}/LC_MESSAGES/'.format(lang))
                if not path.isdir(dirname):
                    makedirs(dirname)
                mofile = path.join(dirname, 'stamp.mo')
                print()
                print('Compile {}'.format(pofile))
                status = system('%s -cv %s --output-file=%s 2>&1' %
                                (msgfmt, pofile, mofile))
                assert status == 0, 'msgfmt failed!'
                self.mofiles.append(mofile)

    def get_outputs(self, *args, **kwargs):
        return _build_py.get_outputs(self, *args, **kwargs) + self.mofiles


setup(
    name='stamp',
    version=VERSION,
    description='Register and keep track of work hours in terminal.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/arivarton/stamp/',
    author='arivarton',
    author_email='packager@arivarton.com',
    license='GNU GPL v3',
    cmdclass={'build_py': build_py},
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
    install_requires=install_requires,
    packages=find_packages(exclude=['tests', 'locale']),
    entry_points={
        'console_scripts': [
            'stamp = stamp.stamp:run',
        ]
    }
)
