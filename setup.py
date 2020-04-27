
from os.path import join
from setuptools import setup, find_packages

setup(name='rec_room',
      version='0.1.0',
      description='Rec Room',
      author='jdpena',
      classifier=['Private :: Do Not Upload'],
      license='This software is provided on an As-Is basis.',
      entry_points={
        'console_scripts': [
            'rec = rec_room.__main__:main'
        ]
    },
    package_dir={'rec_room': 'rec_room'},
    package_data={'': [join('resources', '*'), join('resources', '.*')]},
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*']),
    install_requires=[
        'Flask==1.1.1',
        'flask-restful==0.3.8', 
        'flask-cors==3.0.8',
        'pandas==1.0.1',
        'numpy==1.18.1',
        'scikit-learn==0.22.2',
        'scipy==1.4.1',
        'joblib==0.14.1',
        'pyyaml==5.3.1'
    ],
    extras_require={
        'docs': [
            'Sphinx==1.4.4',
            'docutils',
            'sphinx_py3doc_enhanced_theme',
            'sphinx-pypi-upload'
        ]
    }
)