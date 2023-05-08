# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""`RoleNeed`s for permission policies.

To use these roles, add them to the database via:
    `$ invenio roles create oer_certified_user`
    `$ invenio roles create oer_curator`
then assign roles to users via:
    `$ invenio roles add user@email.com oer_certified_user`
"""

from flask_principal import RoleNeed

# using `flask_principal.RoleNeed`` instead of `invenio_access.SystemRoleNeed`,
# because these roles are assigned by an admin rather than automatically by the system
oer_certified_user = RoleNeed("oer_certified_user")
oer_curator = RoleNeed("oer_curator")
