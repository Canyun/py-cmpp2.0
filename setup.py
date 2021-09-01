from setuptools import setup, find_namespace_packages

version = '2.0.2'
name = 'pycmpp'

setup(
    name=name,
    version=version,
    packages=find_namespace_packages(include=["pycmpp"]),
    install_requires=[
    ],
    python_requires=">=3.7",
    url="https://github.com/Canyun/py-cmpp2.0",
    include_package_data=True,
    license='GNU General Public License v3.0',
    author='Lee',
    author_email='canyun@live.com',
    description=f'移动短信网关cmpp2.0',
)
