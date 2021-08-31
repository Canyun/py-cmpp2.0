from setuptools import setup, find_namespace_packages

version = '2.0.0'
name = 'pycmpp'

setup(
    name=name,
    version=version,
    packages=find_namespace_packages(include=["pycmpp"]),
    install_requires=[
    ],
    include_package_data=True,
    license='GNU General Public License v3.0',
    author='Lee',
    author_email='canyun@live.com',
    description=f'移动短信网关cmpp2.0',
)
