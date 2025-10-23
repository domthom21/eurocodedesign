=====
Getting started
=====

To use eurocodedesign in a project::

    import eurocodedesign as ed

Currently, the development mainly focuses on the implementation of steel verification methods in python for research with no guarantee for correctness.


Basic library structure
-----------------------

eurocodedesign.core
    Contains type declarations and core functionality, e.g. national annex support and si types
eurocodedesign.constants
    Defines basic engineering constants
eurocodedesign.geometry
    Defines basic (steel) sections, focusing on geometries
eurocodedesign.materials
    Defines basic (steel) material, focusing on materials like S235, S355 etc.
eurocodedesign.standard.*
    Contains the python implementation of methods defined in standards, mainly Eurocode 3 (ec3).
eurocodedesign.stepper
    Helper function to accept step descriptions while applying verification methods and prints them.
