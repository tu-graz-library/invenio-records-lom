..
    Copyright (C) 2020 Graz University of Technology.

    invenio-records-lom is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Installation
============

invenio-records-lom is on PyPI so all you need is:

.. code-block:: console

    $ pip install invenio-records-lom

Normally, your instance will specify the correct dependency on your database
and Elasticsearch version you use. If not, you can explict install the
dependencies via the following extra install targets:

- ``elasticsearch7``
- ``postgresql``

For instance:

.. code-block:: console

    $ pip install invenio-records-lom[elasticsearch7]
