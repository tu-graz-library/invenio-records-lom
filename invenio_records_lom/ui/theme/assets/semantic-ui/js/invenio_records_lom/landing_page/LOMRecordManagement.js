// This file is part of invenio-records-lom
// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import React, { useState } from "react";
import { http } from "react-invenio-forms";
import { Button, Grid, Icon, Message } from "semantic-ui-react";

// TODO: figure out where to import i18next from...
const i18next = { t: (text) => text };

const EditButton = ({ recid, onError }) => {
  const [loading, setLoading] = useState(false);

  const editThenRedirect = async () => {
    setLoading(true);
    try {
      await http.post(`/api/lom/${recid}/draft`);
      window.location = `/lom/uploads/${recid}`;
    } catch (error) {
      setLoading(false);
      onError(error.response.data.message);
    }
  };

  return (
    <Button
      className="warning"
      fluid
      icon
      labelPosition="left"
      loading={loading}
      onClick={editThenRedirect}
      size="medium"
    >
      <Icon name="edit" />
      {i18next.t("Edit")}
    </Button>
  );
};

export const LOMRecordManagement = ({
  currentUserId,
  isDraft,
  permissions,
  record,
}) => {
  const [error, setError] = useState("");

  return (
    <Grid columns={1} className="recordMangement">
      {permissions.can_edit && !isDraft && (
        <Grid.Column>
          <EditButton
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
