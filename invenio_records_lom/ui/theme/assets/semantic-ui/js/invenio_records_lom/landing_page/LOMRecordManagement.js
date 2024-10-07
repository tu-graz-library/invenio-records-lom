// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { EditButton } from "@js/invenio_records_lom/components/EditButton";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Grid, Message } from "semantic-ui-react";

export const LOMRecordManagement = ({ isDraft, permissions, record }) => {
  const [error, setError] = useState("");

  return (
    <Grid columns={1} className="recordMangement">
      {permissions.can_edit && !isDraft && (
        <Grid.Column>
          <EditButton
            fluid
            className="warning"
            size="medium"
            recid={record.id}
            onError={(message) => setError(message)}
          />
        </Grid.Column>
      )}
      {error && (
        <Grid.Row className="record-management">
          <Grid.Column>
            <Message negative>{error}</Message>
          </Grid.Column>
        </Grid.Row>
      )}
    </Grid>
  );
};

LOMRecordManagement.propTypes = {
  isDraft: PropTypes.bool.isRequired,
  permissions: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
};
