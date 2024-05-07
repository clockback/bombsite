.. image:: https://raw.githubusercontent.com/clockback/bombsite/master/src/bombsite/images/logo/bombsite.svg
   :align: center

Bombsite is a free and open-source video game inspired by WarMUX, itself inspired by Worms. The player commands a collection of characters who battle against other teams in a turn-based artillery game.

Installation
============

The primary way to install Bombsite is via Debian package. At present, these can be found `here <https://github.com/clockback/bombsite/releases/latest>`_.
Alternatively, Bombsite can be installed as a Python package using the wheel from the same location. In this case, it is recommended that it is installed with ``pipx``.

Development
===========

To clone the repository:

.. code-block:: sh

   $ git clone https://github.com/clockback/bombsite.git

To create a development environment, a virtual environment should be created with a Python version of at least 3.11. Once this is done, to install the package:

.. code-block:: sh

   $ python -m pip install -r requirements-dev.txt -e .

A wheel distribution can be built like so:

.. code-block:: sh

   $ python -m build

A Debian package can be built like so:

.. code-block:: sh

   $ dpkg-buildpackage -b -uc -us -rfakeroot

Quality checks
--------------

The following commands should be used to ensure that the code is acceptable:

.. code-block:: sh

   $ python -m ruff check src/
   $ python -m ruff format --check src/
   $ python -m mypy src/

These checks must pass before being integrated into the master branch.
