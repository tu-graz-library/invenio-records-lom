// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { getInputFromDOM } from "@js/invenio_rdm_records";
import React from "react"; // needs be in scope to use .jsx
import ReactDOM from "react-dom";
import LOMDepositForm from "./LOMDepositForm";

ReactDOM.render(
  <LOMDepositForm
    config={getInputFromDOM("lom-deposit-config")}
    files={getInputFromDOM("lom-deposit-files")}
    record={getInputFromDOM("lom-deposit-record")}
    permissions={getInputFromDOM("lom-deposit-record-permissions")}
  />,
  document.getElementById("lom-deposit-form")
);
