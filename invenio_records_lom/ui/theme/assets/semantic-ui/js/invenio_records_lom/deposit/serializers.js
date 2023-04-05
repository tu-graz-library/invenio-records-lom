// This file is part of invenio-records-lom
// Copyright (C) 2022 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _cloneDeep from "lodash/cloneDeep";
import _get from "lodash/get";
import _groupBy from "lodash/groupBy";
import _pick from "lodash/pick";
import _set from "lodash/set";
import _sortBy from "lodash/sortBy";
import { DepositRecordSerializer } from "react-invenio-deposit";

const debug = (obj) => alert(JSON.stringify(obj, null, 2));

export class LOMDepositRecordSerializer extends DepositRecordSerializer {
  constructor(locale, vocabularies) {
    super();
    this.locale = locale;
    this.vocabularies = vocabularies;
  }

  deserializeOefos(recordToDeserialize) {
    const oefosClassification = _get(
      recordToDeserialize,
      "metadata.classification",
      []
    ).find(
      (classification) =>
        _get(classification, "purpose.value.langstring.#text") === "discipline"
    );
    if (!oefosClassification) {
      _set(recordToDeserialize, "metadata.form.oefos", []);
      return;
    }
    let oefosIds = [];
    for (const taxonpath of _get(oefosClassification, "taxonpath", [])) {
      for (const taxon of _get(taxonpath, "taxon", [])) {
        const match =
          /https:\/\/w3id.org\/oerbase\/vocabs\/oefos2012\/(\d+)/.exec(
            taxon.id || ""
          );
        if (match) {
          const id = match[1];
          if (!oefosIds.includes(id)) {
            oefosIds.push(id);
          }
        }
      }
    }
    oefosIds.sort();
    _set(
      recordToDeserialize,
      "metadata.form.oefos",
      oefosIds.map((oefosId) => ({ value: oefosId }))
    );
  }

  serializeRemoveKeys(recordToSerialize, path = "metadata") {
    // remove `__key`
    const value = _get(recordToSerialize, path);
    if (typeof value === "object" && value !== null) {
      const valueIsArray = Array.isArray(value);
      for (const [key, subValue] of Object.entries(value)) {
        if (valueIsArray) {
          delete subValue.__key;
        }
        this.serializeRemoveKeys(recordToSerialize, `${path}.${key}`);
      }
    }
  }

  serializeContributor(recordToSerialize) {
    // contributes need be grouped by role
    // of form [ {role: {value: <role:str>}, name: <name:str>}, ... ]
    const metadata = recordToSerialize?.metadata || {};
    const formContributors = _get(metadata, "form.contributor", []);
    const groupedContributors = _groupBy(formContributors, "role.value");
    const metadataContributors = Object.entries(groupedContributors).map(
      ([role, contributorList]) => {
        // _groupBy converts role.value to string, unchosen role becomes "undefined"
        role = role !== "undefined" ? role : "";
        const contribute = {
          role: {
            source: { langstring: { "#text": "LOMv1.0", lang: "x-none" } },
            value: { langstring: { "#text": role || "", lang: "x-none" } },
          },
        };
        contribute.entity = contributorList.map(({ name }) => name || "");
        return contribute;
      }
    );
    _set(metadata, "lifecycle.contribute", metadataContributors);
  }

  serializeOefos(recordToSerialize) {
    // convert `metadata.oefos` to a `metadata.classification` of purpose `discipline`
    // find oefos-values that aren't prefix to other oefos-values
    const metadata = recordToSerialize.metadata || {};
    const frontendOefos = _get(metadata, "form.oefos", []);
    const oefosValues = frontendOefos
      .filter((valueDict) => valueDict.value)
      .map((valueDict) => String(valueDict.value));
    const sortedOefosValues = _sortBy(
      oefosValues,
      (key) => -key.length, // sort longest first
      (key) => key // for equal length, sort lower numbers first
    );
    let longestOefosValues = [];
    for (const value of sortedOefosValues) {
      if (!longestOefosValues.some((longest) => longest.startsWith(value))) {
        longestOefosValues.push(value);
      }
    }
    longestOefosValues.sort();

    // guarantee existence of metadata.classification
    if (!metadata.classification) {
      metadata.classification = [];
    }
    // remove old oefos, if existent
    metadata.classification = metadata.classification.filter(
      (classification) =>
        !(
          _get(classification, "purpose.value.langstring.#text") ===
          "discipline"
        )
    );
    // create oefos-classification
    let oefosClassification = {
      purpose: {
        source: { langstring: { lang: "x-none", "#text": "LOMv1.0" } },
        value: { langstring: { lang: "x-none", "#text": "discipline" } },
      },
      taxonpath: [],
    };
    // append one taxonpath per longest oefos-value
    for (const value of longestOefosValues) {
      const path = [1, 3, 4, 6]
        .filter((len) => len <= value.length)
        .map((len) => value.slice(0, len));
      oefosClassification.taxonpath.push({
        source: {
          langstring: {
            lang: "x-none",
            "#text": "https://w3id.org/oerbase/vocabs/oefos2012",
          },
        },
        taxon: path.map((oefosId) => ({
          id: `https://w3id.org/oerbase/vocabs/oefos2012/${oefosId}`,
          entry: {
            langstring: {
              // no `lang`, as per LOM-UIBK
              "#text": _get(this.vocabularies.oefos, oefosId).value,
            },
          },
        })),
      });
    }

    // prepend oefos-classification
    metadata.classification.unshift(oefosClassification);
  }

  // backend->frontend
  deserialize(record) {
    // remove information for internal workings of database
    record = _pick(_cloneDeep(record), [
      "access",
      "custom_fields",
      "expanded",
      "files",
      "id",
      "is_published",
      "links",
      "metadata",
      "parent",
      "pids",
      "resource_type",
      "status",
      "ui",
      "versions",
    ]);
    if (!record.metadata) {
      record.metadata = {};
    }
    const metadata = record.metadata;
    metadata.form = {};
    const form = metadata.form;

    // deserialize title
    form.title = _get(metadata, "general.title.langstring.#text", "");

    // deserialize license
    form.license = { value: _get(metadata, "rights.url", "") };

    // deserialize contributors
    const validRoles = Object.keys(_get(this, "vocabularies.contributor", {}));
    form.contributor = [];
    for (const contribute of _get(metadata, "lifecycle.contribute", [])) {
      let role = _get(contribute, "role.value.langstring.#text", "");
      role = validRoles.includes(role) ? role : "";
      for (const name of contribute.entity || []) {
        form.contributor.push({ role: { value: role }, name });
      }
    }

    // deserialize oefos
    this.deserializeOefos(record);

    // deserialize description
    form.description = _get(
      metadata,
      "general.description.0.langstring.#text",
      ""
    );

    // deserialize tags
    const tagLangstringObjects = _get(metadata, "general.keyword", []);
    form.tag = tagLangstringObjects.map((langstringObject) => ({
      value: _get(langstringObject, "langstring.#text", ""),
    }));

    // deserialize language
    form.language = { value: _get(metadata, "general.language.0", "") };

    return record;
  }

  // frontend->backend
  serialize(record) {
    const recordToSerialize = _cloneDeep(record);
    const metadata = recordToSerialize.metadata || {};

    // remove `__key` from array-items
    this.serializeRemoveKeys(recordToSerialize);

    // serialize title
    _set(metadata, "general.title", {
      langstring: {
        "#text": _get(metadata, "form.title", ""),
        lang: this.locale,
      },
    });

    // serialize license
    const licenseUrl = _get(metadata, "form.license.value", "");
    _set(metadata, "rights", {
      copyrightandotherrestrictions: {
        source: { langstring: { "#text": "LOMv1.0", lang: "x-none" } },
        value: { langstring: { "#text": "yes", lang: "x-none" } },
      },
      url: licenseUrl,
      description: {
        langstring: {
          "#text": licenseUrl,
          lang: "x-t-cc-url",
        },
      },
    });

    // serialize contributors
    this.serializeContributor(recordToSerialize);

    // serialize oefos
    this.serializeOefos(recordToSerialize);

    // serialize description
    const description = metadata?.form?.description || "";
    if (description) {
      _set(metadata, "general.description.0", {
        langstring: { "#text": description, lang: this.locale },
      });
    } else {
      _set(metadata, "general.description", []);
    }

    // serialize tags
    const tags = metadata?.form?.tag || [];
    _set(
      metadata,
      "general.keyword",
      tags
        .filter(({ value }) => value)
        .map(({ value }) => ({
          langstring: { "#text": value, lang: this.locale },
        }))
    );

    // serialize language
    const language = metadata?.form?.language?.value || "";
    if (language) {
      _set(metadata, "general.language.0", language);
    } else {
      _set(metadata, "general.language", []);
    }

    delete metadata.form;
    // TODO: remove extraneous fields from record...
    // debug({ recordToSerialize });
    return recordToSerialize;
  }

  // backend->frontend
  deserializeErrors(errors) {
    // [{field: .., messages: ..}] ~> {field: messages.joined}
    // debug({ type: "before error-deserialization", errors });
    let deserializedErrors = {};

    for (const e of errors) {
      _set(deserializedErrors, e.field, e.messages.join(" "));
    }

    // deserialize error for title
    const titleError = _get(deserializedErrors, "metadata.general.title", null);
    if (titleError) {
      _set(deserializedErrors, "metadata.form.title", titleError);
    }

    // deserialize error for license
    const licenseErrorMessages = [];
    for (const { field, messages } of errors) {
      if (String(field).startsWith("metadata.rights")) {
        licenseErrorMessages.push(...messages);
      }
    }
    const licenseErrorMessage = licenseErrorMessages.join(" ");
    if (licenseErrorMessage) {
      _set(
        deserializedErrors,
        "metadata.form.license",
        licenseErrorMessages.join(" ")
      );
    }

    // deserialize error for contribute
    const contributeError = _get(
      deserializedErrors,
      "metadata.lifecycle.contribute",
      null
    );
    if (contributeError) {
      _set(deserializedErrors, "metadata.form.contribute", contributeError);
    }

    // deserialize error for oefos
    const classificationErrorMessages = errors
      .filter((error) =>
        String(error.field || "").startsWith("metadata.classification")
      )
      .map((error) => error.messages || [])
      .flat();
    if (classificationErrorMessages.length > 0) {
      _set(
        deserializedErrors,
        "metadata.form.oefos",
        classificationErrorMessages.join(" ")
      );
    }

    // add error for debug-purposes
    /*deserializedErrors["metadata"] = {
      // "general.title.langstring.lang": "deserialization-error",
      general: {
        title: { langstring: { lang: "title-lang error" } },
        description: {
          0: { langstring: { lang: "desc-lang error" } },
          1: { langstring: { "#text": "desc-text-error" } },
        },
      },
      lifecycle: { version: { langstring: { "#text": "version-text error" } } },
    };*/

    return deserializedErrors;
  }
}
