import setuptools
setuptools.setup(
     name='omnivore_backup',  
     version='0.1',
     entry_points={
         'console_scripts': ['omnivore_backup=omnivore_backup:main'],
     },
     author='Daniel Margolis',
     author_email='dan@af0.net.',
     description='Backup Omnivore to local disk',
     long_description=open('README.md', 'r').read(),
     long_description_content_type='text/markdown',
     url='https://github.com/danmarg/omnivore_backup',
     packages=setuptools.find_packages(
         include=['omnivore_backup', 'omnivore_backup.*'],
     ),
     classifiers=[
         'Programming Language :: Python :: 3',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
     ],
     install_requires=[
         'omnivoreql',
    ],
 )
