// Copyright (C) 2022-2024 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_records_lom/i18next";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { http } from "react-invenio-forms";
import { Button } from "semantic-ui-react";

export const EditButton = ({
  recid,
  onError,
  // the following arguments are for UI:
  className,
  compact,
  floated,
  fluid,
  size,
}) => {
  const [loading, setLoading] = useState(false);

  const editThenRedirect = async () => {
    console.log("editThenRedirect");
    setLoading(true);
    try {
      await http.post(
        `/api/oer/${recid}/draft`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/vnd.inveniolom.v1+json",
          },
        }
      );
      window.location = `/oer/uploads/${recid}`;
    } catch (error) {
      setLoading(false);
      onError(error.response.data.message);
    }
  };

  return (
    <Button
      className={className}
      compact={compact}
      content={i18next.t("Edit")}
      floated={floated}
      fluid={fluid}
      icon="edit"
      labelPosition="left"
      loading={loading}
      onClick={() => editThenRedirect()}
      size={size}
    />
  );
};

EditButton.propTypes = {
  className: PropTypes.string,
  compact: PropTypes.bool,
  floated: PropTypes.string,
  fluid: PropTypes.bool,
  onError: PropTypes.func.isRequired,
  recid: PropTypes.string.isRequired,
  size: PropTypes.string,
};

EditButton.defaultProps = {
  className: null,
  compact: false,
  floated: null,
  fluid: false,
  size: null,
};
