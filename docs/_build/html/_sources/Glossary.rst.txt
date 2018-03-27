Glossary
--------

.. glossary::

    grid
        Used to refer to the simulation area that is stored in memory as a matrix, for quick referencing. If no RAM
        optimisations have been performed, this will be the same as the sample map. If also no sample map is used, this
        will be the same as the fine map.

    sample map
        The map file containing the points to be sampled from. This is the most zoomed in level of the simulation, and
        should encompass all starting locations of lineages.

    fine map
        The map file at a higher resolution (the same as the sample grid) which covers the area lineages are most likely
        to move to, or where a higher spatial resolution is considered important.

    coarse map
        The map file at a lower resolution (specified by the scale) which covers a larger area than the fine map. This is
        to allow lineages to move far from their starting positions if required.

    pristine map
        A historic map containing population densities at those times. Both fine and coarse pristine maps can be declared
        and multiple sets of pristine maps can be declared at unique times.