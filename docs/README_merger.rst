.. _`merging_simulations`:
Merging simulation outputs
==========================

Introduction
------------
Simulations can be merged using the :class:`Merger class <pycoalescence.merger.Merger>`. Here, multiple simulations are
combined into a single database, with each simulation being associated with a particular "guild". These guilds could
represent different environmental niches, body sizes or other differentiating factors.



Usage
-----

Add simulations using :func:`add_simulation() <pycoalescence.merger.Merger.add_simulation>` and then use
:func:`write() <pycoalescence.merger.Merger.write>`.

Previously calculated metrics are all stored in *_GUILDS tables. Species identities are preserved (without allowing for
a species to exist in more than one guild), meaning all metrics can be re-calculated using
:func:`apply_speciation() <pycoalescence.coalescence_tree.CoalescenceTree.apply_speciation>` and functions such
as :func:`calculate_richness() <pycoalescence.coalescence_tree.CoalescenceTree.calculate_richness>`.
Alternatively, use :func:`add_simulations() <pycoalescence.merger.Merger.add_simulations>`


.. code-block:: python

    merger = Merger("output.db")
    merger.add_simulation("input1.db")
    merger.add_simulation("input2.db")
    merger.write()