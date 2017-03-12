from setuptools import setup

setup(name='awstools',
      version='0.1',
      description='Simple API for AWS IoT',
      url='https://github.com/h314to/awstools',
      author='Filipe Agapito',
      author_email='filipe.agapito@gmail.com',
      license='MIT',
      packages=['awstools'],
      install_requires=[
            'awscli',
            'sh',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
