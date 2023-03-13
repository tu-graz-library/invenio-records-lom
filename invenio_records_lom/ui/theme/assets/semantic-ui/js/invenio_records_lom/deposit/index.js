// This file is part of InvenioRDM
// Copyright (C) 2022 Graz University of Technology.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react"; // needs be in scope to use .jsx
import ReactDOM from "react-dom";
import { getInputFromDOM } from "react-invenio-deposit";
import LOMDepositForm from "./LOMDepositForm";

ReactDOM.render(
  <LOMDepositForm
    config={getInputFromDOM("lom-deposit-config")}
    files={getInputFromDOM("lom-deposit-files")}
    record={getInputFromDOM("lom-deposit-record")}
  />,
  document.getElementById("lom-deposit-form")
);
