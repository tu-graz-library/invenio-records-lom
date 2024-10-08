// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { DepositRecordSerializer } from "@js/invenio_rdm_records";
import _cloneDeep from "lodash/cloneDeep";
import _get from "lodash/get";
import _pick from "lodash/pick";
import _set from "lodash/set";
import _sortBy from "lodash/sortBy";

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
        const match = /https:\/\/w3id.org\/oerbase\/vocabs\/oefos2012\/(\d+)/.exec(
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

    // this sorts lexigraphically, not numerically
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
    // contribution metadata is stored in frontend at `metadata.form.contributor`
    // it is of form [ {role: {value: String}, name: String}, ... ]
    //   in the above: role, name need not exist
    // it needs to be serialized to `metadata.lifecycle.contribute`
    // serialized data is of form [{role: <LOM-vocabulary with value=role>, entity: [String]}]
    const metadata = recordToSerialize?.metadata || {};
    const formContributors = _get(metadata, "form.contributor", []);
    const metadataContributors = formContributors.map(
      ({ role: maybeRoleDict, name: maybeName }) => ({
        role: {
          source: { langstring: { "#text": "LOMv1.0", "lang": "x-none" } },
          value: {
            langstring: { "#text": maybeRoleDict?.value || "", "lang": "x-none" },
          },
        },
        entity: [maybeName || ""],
      })
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
    // filter out classification that previously held oefos, if any
    metadata.classification = metadata.classification.filter(
      (classification) =>
        !(_get(classification, "purpose.value.langstring.#text") === "discipline")
    );
    // create oefos-classification
    let oefosClassification = {
      purpose: {
        source: { langstring: { "lang": "x-none", "#text": "LOMv1.0" } },
        value: { langstring: { "lang": "x-none", "#text": "discipline" } },
      },
      taxonpath: [],
    };
    // append one taxonpath per longest oefos-value
    for (const value of longestOefosValues) {
      // if value === "2074", path is ["2", "207", "2074"]
      const path = [1, 3, 4, 6]
        .filter((len) => len <= value.length)
        .map((len) => value.slice(0, len));
      oefosClassification.taxonpath.push({
        source: {
          langstring: {
            "lang": "x-none",
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

    // initialize; data relevant to upload-form is stored in `metadata.form`
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

    // deserialize format
    form.format = { value: _get(metadata, "technical.format.0", "") };

    // deserialize resource-type
    form.resourcetype = {
      value: _get(metadata, "educational.learningresourcetype.id", ""),
    };

    // deserialize contributors
    const validRoles = Object.keys(_get(this, "vocabularies.contributor", []));
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
    form.description = _get(metadata, "general.description.0.langstring.#text", "");

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
    const recordToSerialize = _pick(_cloneDeep(record), [
      "access",
      "custom_fields",
      // exclude `expanded`
      "files",
      "id",
      // exclude `is_published`
      "links",
      "metadata", // contains `form` for now, excluded later
      "parent",
      "pids",
      "resource_type",
      // exclude `status`
      // exclude `versions`
    ]);
    const metadata = recordToSerialize.metadata || {};

    // remove `__key` from array-items
    this.serializeRemoveKeys(recordToSerialize);

    // serialize title
    _set(metadata, "general.title", {
      langstring: {
        "#text": _get(metadata, "form.title", ""),
        "lang": this.locale,
      },
    });

    // serialize license
    const licenseUrl = _get(metadata, "form.license.value", "");
    const licenseInnerLangstring = { "#text": licenseUrl };
    if (licenseUrl.startsWith("https://creativecommons.org/")) {
      licenseInnerLangstring["lang"] = "x-t-cc-url";
    }
    _set(metadata, "rights", {
      copyrightandotherrestrictions: {
        source: { langstring: { "#text": "LOMv1.0", "lang": "x-none" } },
        value: { langstring: { "#text": "yes", "lang": "x-none" } },
      },
      url: licenseUrl,
      description: {
        langstring: licenseInnerLangstring,
      },
    });

    // serialize format
    const format = _get(metadata, "form.format.value", "");
    _set(metadata, "technical.format.0", format);

    // set location
    _set(
      metadata,
      "technical.location.#text",
      _get(recordToSerialize, "links.record_html", "")
    );

    // serialize resource-type
    const resourcetypeUrl = _get(metadata, "form.resourcetype.value", "");
    _set(metadata, "educational.learningresourcetype", {
      source: {
        langstring: {
          "#text": "https://w3id.org/kim/hcrt/scheme",
          "lang": "x-none",
        },
      },
      id: resourcetypeUrl,
    });

    // serialize contributors
    this.serializeContributor(recordToSerialize);

    // serialize oefos
    this.serializeOefos(recordToSerialize);

    // serialize description
    const description = metadata?.form?.description || "";
    if (description) {
      _set(metadata, "general.description.0", {
        langstring: { "#text": description, "lang": this.locale },
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
          langstring: { "#text": value, "lang": this.locale },
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
    return recordToSerialize;
  }

  // backend->frontend
  deserializeErrors(errors) {
    let deserializedErrors = {};

    // [{field: .., messages: ..}] ~> {field: messages.join(" ")}
    for (const e of errors) {
      _set(deserializedErrors, e.field, e.messages.join(" "));
    }

    // utility to set errors matching a regexp to `metadata.form`
    const setErrors = (regexp, targetKey) => {
      const errorMessage = errors
        .filter(({ field }) => regexp.test(field))
        .flatMap(({ messages }) => messages || [])
        .join(" ");
      if (errorMessage) {
        _set(deserializedErrors, `metadata.form.${targetKey}`, errorMessage);
      }
    };

    // set single-field errors
    setErrors(/^metadata\.general\.title$/, "title");
    setErrors(/^metadata\.rights\.url/, "license.value");
    setErrors(/^metadata\.technical\.format/, "format.value");
    setErrors(
      /^metadata\.educational\.learningresourcetype\.id$/,
      "resourcetype.value"
    );

    // set array-errors
    // TODO: contributor-errors
    //       finding the correct index for `contributor`-errors is non-trivial as the data gets flattened
    //       i.e. an error at "contribute.1.entity.0"'s index depends on how many `entity`s there are in "contribute.0.entity"...
    setErrors(/^metadata\.lifecycle\.contribute$/, "contributor"); // assign all sub-errors to `ArrayField` for now...

    // serialization of OEFOS removes empty and incorrect fields
    // only possible error left is when no OEFOS where provided, set that to `ArrayField`-path
    setErrors(/^metadata\.classification/, "oefos");

    // empty tags are removed by serialization, providing no tags is allowed
    // hence no errors wrt tags should ever occur
    setErrors(/^metadata\.general\.keyword/, "tag");

    // add error for debug-purposes
    /*deserializedErrors["metadata"]["form"] = {
      // "general.title.langstring.lang": "deserialization-error",
      title: "title-lang error",
      contributor: {
        0: { name: "name error" },
        1: { role: { value: "error" } },
      },
    };*/

    return deserializedErrors;
  }
}
