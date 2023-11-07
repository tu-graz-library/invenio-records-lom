// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import { Button, Icon } from "semantic-ui-react";
import { http } from "react-invenio-forms";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_records_lom/i18next";

export const EditButton = ({ recid, onError, className, size, fluid }) => {
  const [loading, setLoading] = useState(false);

  size = size || "small";
  fluid = fluid || false;

  const editThenRedirect = async () => {
    console.log("editThenRedirect");
    setLoading(true);
    try {
      await http.post(`/api/oer/${recid}/draft`);
      window.location = `/oer/uploads/${recid}`;
    } catch (error) {
      setLoading(false);
      onError(error.response.data.message);
    }
  };

  return (
    <Button
      compact
      fluid={fluid}
      className={className}
      size={size}
      floated="right"
      onClick={() => editThenRedirect()}
      icon="edit"
      content={i18next.t("Edit")}
    />
  );
};
