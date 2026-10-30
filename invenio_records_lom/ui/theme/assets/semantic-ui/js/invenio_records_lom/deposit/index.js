/*
 * SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

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
