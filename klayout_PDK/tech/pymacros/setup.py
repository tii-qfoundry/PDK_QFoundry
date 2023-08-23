import os
from importlib.util import module_from_spec, spec_from_file_location
from setuptools import setup, find_packages


# Loads _version.py module without importing the whole package.
def get_version_and_cmdclass(package_name):
    spec = spec_from_file_location('version', os.path.join(package_name, '_version.py'))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.cmdclass

packages=packages=['starfish']
#version, cmdclass = get_version_and_cmdclass('starfish')
version = '0'


setup(
    name='starfish',
    package_dir = {"starfish": "starfish"},
    description="Starfish is a KLayout/Python-based superconducting quantum circuit PDK that works with KQcircuits, developed by TII.",
    author="TII-QRC",
    packages=packages,
    python_requires=">=3.6.9",
)
