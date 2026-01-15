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
if sys.platform != 'win32':
    extra_compile_args = ['-O3', '-Wall', '-Wextra']

btree_module = Extension(
    'btree',
    sources=['src/btreemodule.c'],
    include_dirs=['include'],
    extra_compile_args=extra_compile_args,
)

setup(
    name='btree',
    version='1.0.0',
    description='B-Tree data structure implemented in C for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Alberto',
    author_email='alberto.azzari@protonmail.com',
    url='https://github.com/irazza/btree',
    license='MIT',
    ext_modules=[btree_module],
    python_requires='>=3.11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
