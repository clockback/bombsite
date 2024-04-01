========
Bombsite
========

Bombsite is a free and open-source video game inspired by WarMUX, itself inspired by Worms. The player commands a collection of characters who battle against other teams in a turn-based artillery game.

Installation
============

There are no releases of Bombsite at present.

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

Quality checks
--------------

The following commands should be used to ensure that the code is acceptable:

.. code-block:: sh

   $ python -m pylint --rcfile=.settings/pylintrc src/
   $ python -m mypy src/

These checks must pass before being integrated into the master branch.
