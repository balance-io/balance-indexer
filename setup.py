from setuptools import setup, find_packages

setup(
  name='balance-indexer',
  version="0.1",
  install_requires=[
    'aiohttp',
    'aioredis',
    'uvloop',
    'redis',
  ],
  packages=find_packages(),
  entry_points={
    'console_scripts': ['balance-indexer=balance_indexer:main',]
  },
)
