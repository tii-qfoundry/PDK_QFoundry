import os
from importlib.util import module_from_spec, spec_from_file_location
from setuptools import setup, find_packages


# Loads _version.py module without importing the whole package.
def get_version_and_cmdclass(package_name):
    spec = spec_from_file_location('version', os.path.join(package_name, '_version.py'))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.cmdclass


version, cmdclass = get_version_and_cmdclass('starfish')

setup(
    name='starfish',
    version=version,
    cmdclass=cmdclass,
    description="starfisk is a KLayout/Python-based superconducting quantum circuit PDK that works with KQcircuits, developed by TII.",
    author="TII-QRC",
    author_email="",
    url="",
    packages=find_packages(),
    python_requires=">=3.6.9",
    install_requires=[                # Record dependencies in kqcircuits/util/dependecies.py too
        "klayout>=0.26",
        "numpy>=1.16",
        "Autologging~=1.3",
        "scipy>=1.2",
        "tqdm>=4.61",
        # psutil was considered when cpu_count(logical=False), was implemented in an alternative way
        # in elmer_export.py and gmsh_helpers.py, consider adding if more features are needed.
    ],
    extras_require={
        "docs": ["sphinx~=4.4", "sphinx-rtd-theme~=0.4", "networkx>=2.7", "matplotlib>=3.5.1"],
        "tests": ["pytest>=6.0.2", "pytest-cov~=2.8", "pytest-xdist>=2.1", "tox>=3.18", "pylint==2.9",
                  "networkx>=2.7", "matplotlib>=3.5.1", "nbqa~=1.3"],
        "notebooks": ["gdspy~=1.5", "jupyter~=1.0.0"],
        "graphs": ["networkx>=2.7", "matplotlib>=3.5.1"],
    },
)
