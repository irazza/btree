#!/usr/bin/env python3
"""
Simple build script that uses only distutils (no setuptools required).
Works with any Python installation that has development headers.

Usage:
    python build.py

This will build the btree extension module in-place.
"""

import sys
import os
import subprocess
import sysconfig

def get_python_include():
    """Get Python include directory."""
    return sysconfig.get_path('include')

def get_python_lib_dir():
    """Get Python library directory."""
    return sysconfig.get_config_var('LIBDIR')

def get_ext_suffix():
    """Get the extension suffix for shared libraries."""
    return sysconfig.get_config_var('EXT_SUFFIX') or '.so'

def main():
    # Source and output files
    src_file = 'src/btreemodule.c'
    include_dir = 'include'
    output_name = 'btree' + get_ext_suffix()
    
    python_include = get_python_include()
    
    print(f"Building btree extension...")
    print(f"  Python include: {python_include}")
    print(f"  Output: {output_name}")
    
    # Compile command
    if sys.platform == 'win32':
        # Windows compilation (MSVC)
        compile_cmd = [
            'cl', '/c', '/O2', '/W3',
            f'/I{include_dir}',
            f'/I{python_include}',
            '/Fosrc/btreemodule.obj',
            src_file
        ]
        link_cmd = [
            'link', '/DLL',
            f'/OUT:{output_name}',
            'src/btreemodule.obj',
            f'/LIBPATH:{get_python_lib_dir()}',
            f'python{sys.version_info.major}{sys.version_info.minor}.lib'
        ]
    else:
        # Unix compilation (gcc/clang)
        compile_cmd = [
            'gcc', '-shared', '-fPIC',
            '-O3', '-Wall', '-Wextra',
            f'-I{include_dir}',
            f'-I{python_include}',
            '-o', output_name,
            src_file
        ]
        
        # On macOS, need different flags
        if sys.platform == 'darwin':
            compile_cmd.insert(1, '-undefined')
            compile_cmd.insert(2, 'dynamic_lookup')
    
    print(f"\n  Command: {' '.join(compile_cmd)}\n")
    
    try:
        result = subprocess.run(compile_cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✓ Successfully built {output_name}")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed!")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return 1
    except FileNotFoundError:
        print("✗ Compiler not found. Make sure gcc (Linux/macOS) or cl (Windows) is installed.")
        return 1

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    sys.exit(main())
