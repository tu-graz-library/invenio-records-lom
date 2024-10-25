// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import $ from "jquery";
import React from "react"; // needs be in scope to use .jsx
import ReactDOM from "react-dom";
import { LOMRecordManagement } from "./LOMRecordManagement";

const recordManagementElement = document.getElementById("lomRecordManagement");

// TODO: use invenio's management React-component instead once they implement configurable API-urls
if (recordManagementElement) {
  ReactDOM.render(
    <LOMRecordManagement
      record={JSON.parse(recordManagementElement.dataset.record)}
      permissions={JSON.parse(recordManagementElement.dataset.permissions)}
      isDraft={JSON.parse(recordManagementElement.dataset.isDraft)}
    />,
    recordManagementElement
  );
}

// enable semantic-ui's accordion-behavior for file-preview and files-list
$("#lom-filelist-accordion").accordion();
$("#lom-filepreview-accordion").accordion();
