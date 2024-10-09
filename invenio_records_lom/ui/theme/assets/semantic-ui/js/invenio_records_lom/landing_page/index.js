// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react"; // needs be in scope to use .jsx
import { createRoot } from "react-dom/client";
import { LOMRecordManagement } from "./LOMRecordManagement";

const recordManagementElement = document.getElementById("lomRecordManagement");

// TODO: use invenio's management React-component instead once they implement configurable API-urls
if (recordManagementElement) {
  const root = createRoot(recordManagementElement);
  root.render(
    <LOMRecordManagement
      record={JSON.parse(recordManagementElement.dataset.record)}
      permissions={JSON.parse(recordManagementElement.dataset.permissions)}
      isDraft={JSON.parse(recordManagementElement.dataset.isDraft)}
    />
  );
}
