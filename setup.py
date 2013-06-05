from setuptools import setup

setup(name='hosts',
      version='0.1',
      description='A small tool for organizing the hosts file',
      url='http://github.com/dhaffner/hosts.py',
      author='Dustin Haffner',
      author_email='dh@xix.org',
      license='MIT',
      packages=['hosts'],
      scripts=['bin/hosts'],
      install_requires=[
          'six', 'baker',
      ],
      zip_safe=False)
