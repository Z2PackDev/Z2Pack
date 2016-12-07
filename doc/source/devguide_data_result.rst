Data containers - ``Result`` and ``Data`` objects
=================================================

Overview - Basic structure
--------------------------

There are two kinds of objects which contain the outcome of a Z2Pack calculation: ``Result`` and ``Data`` objects. The distinction between the two is simple (although the naming is quite arbitrary):

* ``Data`` objects contain only the data produced in a calculation, but not the convergence information.

* ``Result`` objects contain the ``Data`` object **and** the :ref:`Control <devguide_control>` states which store the convergence / iteration information.

The reason for these two distinct kinds of data container is that the :ref:`Control <devguide_control>` objects (which will be discussed later) need to know the outcome of a calculation. For this reason, they are passed the ``Data`` object. To in turn save the state of the :ref:`Control <devguide_control>`, the ``Result`` is needed.

Taking into account that surface calculations contain a series of line calculations, the final structure is this:

* :class:`.SurfaceResult`
    * :class:`.SurfaceData`
        * :class:`.LineResult`
            * :class:`.WccLineData`
            * :class:`.EigenstateLineData`
            
Simplified public interface -- ``__getattr__`` tricks
-----------------------------------------------------
            
This nested structure is quite practical for the internal implementation. However, for the public interface a simpler way to access data attributes is needed. Two tricks are used to allow the end user to get all the data he needs directly from the topmost ``Result`` object:

1. The ``__getattr__`` method of the ``Result`` forwards attribute access (for attributes which don't exist in the ``Result``) to its ``Data`` object.
2. The :class:`.SurfaceData` ``__getattr__`` forwards attribute access to each of the ``LineResult`` objects it contains, returning a list of objects.

With these two tricks, it is possible to just write 

.. code :: python
    
    result = z2pack.surface.run(...)
    print(result.wcc)
    
The ``wcc`` attribute access will be forwarded from the :class:`.SurfaceResult` to the :class:`.SurfaceData`, which forwards it to each of the :class:`.LineResult` objects. Finally, those forward it to the line ``Data`` objects, which contain the ``wcc`` attribute. The result is a list, containing a list of WCC for each line.

:class:`.WccLineData` and :class:`.EigenstateLineData` - lazy properties and the Locker metaclass
-------------------------------------------------------------------------------------------------

The :class:`.WccLineData` and :class:`.EigenstateLineData` classes use two things that might not be obvious at first glance -- lazy properties, and the ``ConstLocker`` metaclass.

First off, the lazy properties: This is a decorator which has two effects

1. The function is a property. That is, accessing the function gives you its returns value, just like the regular ``@property``.
2. When the function has been evaluated for the first time, the attribute is replaced by its value. The purpose of this is to avoid computing the property multiple times.

.. autoclass :: z2pack.line._data._LazyProperty
    :members:
    
The attributes of the line ``Data`` objects have a hierarchical structure (the gap is calculated from the WCC, which is calculated from the Wilson loop, etc.), and the lazy properties are used to easily implement this without having to worry about computing anything twice.

By itself, using the lazy properties has one drawback: The user (or the programmer) could inadvertently change an attribute of the ``Data`` instance. Because the subsequent properties might already be evaluated, this change will not be reflected. Since this is not desired, I decided to forbid changing attributes altogether. This is the purpose of the ``ConstLocker`` metaclass. Its only effect is that it is not possible to change attributes after the ``__init__`` method -- unless the instance is explicitly `unlocked`.
