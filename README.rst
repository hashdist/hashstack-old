python-hpcmp
============

An enhanced Python distribution for HPCMP systems.

NOTE: This is currently work-in-progress on moving python-hpcmp
to use the Hashdist tool.

Usage
-----

Edit the ``config.yml`` file to fit your host. Builds will be performed
with the ``PATH`` given + dependencies from python-hpcmp.

Then, run::

    ./update

or, for more verbose output::

    ./update -v

The resulting software stack will be put in ``local`` (which is a
symlink to a Hashdist "profile" unde ``opt``). To use it, add the
following to your environment::

    export PATH=/path/to/python-hpcmp/local/bin:$PATH
    export LD_LIBRARY_PATH=/path/to/python-hpcmp/local/lib:$LD_LIBRARY_PATH

In time, the need for modifying ``LD_LIBRARY_PATH`` should gradually
disappear.

Power-users guide
-----------------

The available packages are listed in ``package.yml``, which hopefully
should be mostly self-documenting. What controls how a package is
built is the "recipe", e.g., set ``recipe: distutils`` for a
``python setup.py install``-style package.

The ``standard`` recipe is a configure-make-install-style package,
and reads configuration files from files such as
``${package}Config/configure.$arch`` to figure out how to do
the configuration.

The recipes are implemented as Python code that generates Hashdist
build artifacts, and are located in ``builder/recipes.py``. The
builder logic itself (what is not in Hashdist) is in ``builder/builder.py``.

It is anticipated that most of what is described above will eventually
find its way into an (optional) sub-package,  ``hashdist.frontend``,
within Hashdist itself.
