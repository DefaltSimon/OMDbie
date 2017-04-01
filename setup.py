# coding=utf-8
from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='OMDbie',
      version='0.1',
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
      zip_safe=False)
