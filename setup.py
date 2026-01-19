# B-Tree Python Extension
#
# Build and install:
#   pip install .
#
# Or build in-place for development:
#   pip install -e .
#
# Or using setup.py directly:
#   python setup.py build_ext --inplace

from setuptools import setup, Extension
import sys

# Extra compile args based on platform
extra_compile_args = []
extra_link_args = []
if sys.platform != 'win32':
    extra_compile_args = ['-O3', '-Wall', '-Wextra']
else:
    extra_compile_args = ['/O2', '/W3']
    extra_link_args = []

btree_module = Extension(
    'btreedict',
    sources=['src/btreemodule.c'],
    include_dirs=['include'],
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)

setup(
    name='btreedict',
    version='1.0.2',
    description='B-Tree data structure implemented in C as a Python Extension Module',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Alberto',
    author_email='alberto.azzari@protonmail.com',
    url='https://github.com/irazza/btree',
    license='MIT',
    ext_modules=[btree_module],
    python_requires='>=3.12',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
