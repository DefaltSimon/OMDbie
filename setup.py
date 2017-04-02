# coding=utf-8
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


extras = {
    "fast": ["ujson>=1.35"],
    "requests": ["requests>=2.13.0"]
}

setup(name='OMDbie',
      version='1.1.2',
      description='Python API wrapper for OMDb',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Intended Audience :: Developers',
      ],
      url='https://github.com/DefaltSimon/OMDbie',
      author='DefaltSimon',
      license='MIT',
      keywords="defaltsimon omdb api wrapper",
      packages=['omdbie'],
      install_requires=requirements,
      extras_require=extras,
      zip_safe=False)
