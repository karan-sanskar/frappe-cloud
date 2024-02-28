from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in frappe_cloud/__init__.py
from frappe_cloud import __version__ as version

setup(
	name="frappe_cloud",
	version=version,
	description="Frappe Cloud API",
	author="rajvi",
	author_email="rajvi@webisoft.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
