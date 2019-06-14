from setuptools import find_packages, setup

setup(
    name='ViewCraft',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
        'Flask-Babel',
        'Flask-Bootstrap',
        'Flask-HTTPAuth',
        'Flask-Logging',
        'Flask-Login',
        'Flask-Migrate',
        'Flask-Moment',
        'Flask-Mail',
        'Flask-restplus',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'python-dotenv',

    ],
    entry_points={
        'viewcraft_scripts': [
            'viewcraft=app.cli:main',
        ]
    },
    test_suite="tests",
)
