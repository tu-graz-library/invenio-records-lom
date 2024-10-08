// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import axios from "axios";

export const debug = (obj) => alert(JSON.stringify(obj, null, 2));

const DEBUG_BASE_HEADERS = {
  "json": { "Content-Type": "application/json" },
  "vnd+json": {
    "Content-Type": "application/json",
    "Accept": "application/vnd.inveniolom.v1+json",
  },
  "octet-stream": { "Content-Type": "application/octet-stream" },
};
const debugApiConfig = {
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
  headers: DEBUG_BASE_HEADERS.json,
};
const debugAxiosWithConfig = axios.create(debugApiConfig);

class DepositApiClientResponse {
  constructor(data, errors) {
    this.data = data;
    this.errors = errors;
  }
}

export class DebugApiClient {
  constructor(createDraftURL, recordSerializer) {
    this.createDraftURL = createDraftURL;
    this.recordSerializer = recordSerializer;
  }
  async _createResponse(axiosRequest) {
    try {
      const response = await axiosRequest();
      const data = this.recordSerializer.deserialize(response.data || {});
      const errors = this.recordSerializer.deserializeErrors(
        response.data.errors || []
      );
      return new DepositApiClientResponse(data, errors);
    } catch (error) {
      const errorData = error.response.data;
      throw new DepositApiClientResponse({}, errorData);
    }
  }
  async createDraft(draft) {
    const payload = this.recordSerializer.serialize(draft);
    return this._createResponse(() =>
      debugAxiosWithConfig.post(this.createDraftURL, payload, {
        headers: DEBUG_BASE_HEADERS["vnd+json"],
        params: { expand: 1 },
      })
    );
  }
  async saveDraft(draft, draftLinks) {
    const payload = this.recordSerializer.serialize(draft);
    const resp = await this._createResponse(() =>
      debugAxiosWithConfig.put(draftLinks.self, payload, {
        headers: DEBUG_BASE_HEADERS["vnd+json"],
        params: { expand: 1 },
      })
    );
    console.log(resp);
    return resp;
  }
  async publishDraft(draftLinks) {
    return this._createResponse(() =>
      debugAxiosWithConfig.post(draftLinks.publish, {}, { params: { expand: 1 } })
    );
  }

  async deleteDraft(draftLinks) {
    return this._createResponse(() => debugAxiosWithConfig.delete(draftLinks.self, {}));
  }

  async reservePID(draftLinks, pidType) {
    return this._createResponse(() => {
      const link = draftLinks[`reserve_${pidType}`];
      return debugAxiosWithConfig.post(link, {}, { params: { expand: 1 } });
    });
  }

  async discardPID(draftLinks, pidType) {
    return this._createResponse(() => {
      const link = draftLinks[`reserve_${pidType}`];
      return debugAxiosWithConfig.delete(link, { params: { expand: 1 } });
    });
  }

  async createOrUpdateReview(draftLinks, communityId) {
    throw new Error("Not implemented.");
  }

  async deleteReview(draftLinks) {
    throw new Error("Not implemented.");
  }

  async submitReview(draftLinks) {
    throw new Error("Not implemented.");
  }
}
