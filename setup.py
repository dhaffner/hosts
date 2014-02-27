from setuptools import setup

setup(name='hosts',
      version='0.1',
      description='A command line tool for managing hosts files.',
      url='http://github.com/dhaffner/hosts',
      author='Dustin Haffner',
      author_email='dh@xix.org',
      license='MIT',
      packages=['hosts'],
      scripts=['bin/hosts'],
      install_requires=['docopt'],
      zip_safe=False)
