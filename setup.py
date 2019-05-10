#
# This file is part of robospect.py.
#
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
from setuptools import setup, find_packages

setup(
    name="robospect",
    version="0.dev201905",
    author="Christopher Z Waters & Julie Hollek",
    author_email="czw@princeton.edu",
    package_dir={'':'python'},
    packages=find_packages(where="./python/"),
    scripts=["bin/rSpect.py"],
    url="http://www.ifa.hawaii.edu/~watersc1/robospect.html",
    license="LICENSE",
    description="Automated equivalent-width measurement for astronomical spectra",
    long_description="",
    python_requires=">3.6.5",
    install_requires=[
        'numpy',
        'scipy'
    ],
)


