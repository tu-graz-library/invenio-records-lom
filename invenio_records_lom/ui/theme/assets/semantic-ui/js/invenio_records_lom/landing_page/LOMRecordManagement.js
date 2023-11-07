// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import { http } from "react-invenio-forms";
import { Button, Grid, Icon, Message } from "semantic-ui-react";
import { i18next } from "@translations/invenio_records_lom/i18next";
import { EditButton } from "@js/invenio_records_lom/components/EditButton";

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
