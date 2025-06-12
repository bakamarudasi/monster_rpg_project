from setuptools import setup, find_packages

setup(
    name='monster_rpg',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={
        'monster_rpg': [
            'templates/*.html',
            'static/**/*',
            'monsters/*.json',
            'map/*.json',
        ]
    },
)
