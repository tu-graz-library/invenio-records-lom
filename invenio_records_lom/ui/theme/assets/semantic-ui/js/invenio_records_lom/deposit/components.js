// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { PIDField } from "@js/invenio_rdm_records";
import { i18next } from "@translations/invenio_records_lom/i18next";
import React from "react";
import { AccordionField, ArrayField, FieldLabel } from "react-invenio-forms";
import { useSelector } from "react-redux";
import { Form, Icon } from "semantic-ui-react";

import {
  ContributorField,
  DebugInfo,
  DropdownField,
  LeftLabeledTextField,
  TitledTextField,
} from "./fields";

export function RequiredAccordion(props) {
  const record = useSelector((state) => state?.deposit?.record);

  return (
    <AccordionField
      active
      includesPaths={[
        "metadata.general",
        "metadata.general.title.langstring.lang",
        "metadata.general.title.langstring.#text",
      ]}
      label={
        <>
          <Icon
            color="red"
            name="asterisk"
            style={{ float: "left", marginRight: 14 }}
          />
          {i18next.t("Required Fields")}
        </>
      }
    >
      <PIDField
        btnLabelDiscardPID={i18next.t("Cancel DOI reservation.")}
        btnLabelGetPID={i18next.t("Reserve a DOI.")}
        canBeManaged
        canBeUnmanaged
        fieldPath="pids.doi"
        fieldLabel={
          <>
            <Icon color="red" name="asterisk" />
            <Icon name="book" />
            {i18next.t("Digital Object Identifier")}
          </>
        }
        // record.is_published should be one of `true`, `false`, `null` (counts as false)
        isEditingPublishedRecord={record?.is_published === true}
        managedHelpText={i18next.t(
          "Reserved DOIs are registered when publishing your upload."
        )}
        pidIcon={null}
        pidLabel={i18next.t("DOI")}
        pidPlaceholder={i18next.t("Enter your existing DOI here.")}
        pidType="doi"
        record={record}
        required={false} // this field is required, but the red asterisk is added via the fieldLabel prop...
        unmanagedHelpText={i18next.t(
          "A DOI allows your upload to be unambiguously cited. It is of form `10.1234/foo.bar`."
        )}
      />
      <TitledTextField
        fieldPath="metadata.form.title"
        iconName="book"
        placeholder={i18next.t("Enter your title here.")}
        required
        title={i18next.t("Title")}
      />
      <DropdownField
        fieldPath="metadata.form.license"
        iconName="drivers license"
        placeholder={i18next.t("Select License")}
        required
        title={i18next.t("License")}
        vocabularyName="license"
      />
      <DropdownField
        fieldPath="metadata.form.format"
        iconName="tag"
        placeholder={i18next.t("Select Format")}
        required
        title={i18next.t("Format")}
        vocabularyName="format"
      />
      <DropdownField
        fieldPath="metadata.form.resourcetype"
        iconName="tag"
        placeholder={i18next.t("Select Resource Type")}
        required
        title={i18next.t("Resource Type")}
        vocabularyName="resourcetype"
      />
      <ArrayField
        addButtonLabel={i18next.t("Add Contributor")}
        defaultNewValue={{}}
        fieldPath="metadata.form.contributor"
        label={
          // automatically wrapped in <label /> by `ArrayField`
          <>
            <Icon color="red" name="asterisk" />
            <Icon name="user plus" />
            {i18next.t("Contributors")}
          </>
        }
      >
        {({ arrayHelpers, indexPath }) => (
          <ContributorField
            closeAction={() => arrayHelpers.remove(indexPath)}
            fieldPath={`metadata.form.contributor.${indexPath}`}
            vocabularyName="contributor"
          />
        )}
      </ArrayField>
      <ArrayField
        addButtonLabel={i18next.t("Add OEFOS")}
        defaultNewValue={{}}
        fieldPath="metadata.form.oefos"
        label={
          // automatically wrapped in <label /> by `ArrayField`
          <>
            <Icon color="red" name="asterisk" />
            <Icon name="barcode" />
            {i18next.t("OEFOS")}
          </>
        }
      >
        {({ arrayHelpers, indexPath }) => (
          <DropdownField
            closeAction={() => arrayHelpers.remove(indexPath)}
            fieldPath={`metadata.form.oefos.${indexPath}`}
            placeholder={i18next.t("Select OEFOS")}
            vocabularyName="oefos"
          />
        )}
      </ArrayField>
    </AccordionField>
  );
}

export function OptionalAccordion(props) {
  return (
    <AccordionField includesPaths={[]} label={i18next.t("Optional Fields")}>
      <TitledTextField
        fieldPath="metadata.form.description"
        iconName="pencil"
        placeholder={i18next.t("Enter your description here.")}
        rows={5}
        title={i18next.t("Description")}
      />
      <ArrayField
        addButtonLabel={i18next.t("Add Tag")}
        defaultNewValue={{ value: "" }}
        fieldPath="metadata.form.tag"
        label={<FieldLabel icon="tag" label={i18next.t("Tags")} />}
      >
        {({ arrayHelpers, indexPath }) => (
          <TitledTextField
            closeAction={() => arrayHelpers.remove(indexPath)}
            fieldPath={`metadata.form.tag.${indexPath}.value`}
            label={i18next.t("Tag")}
            placeholder={i18next.t("Enter your tag here")}
          />
        )}
      </ArrayField>
      <DropdownField
        clearable
        fieldPath="metadata.form.language"
        iconName="globe"
        placeholder={i18next.t("Select Language")}
        title={i18next.t("Language")}
        vocabularyName="language"
      />
    </AccordionField>
  );
}

export function TestAccordion(props) {
  return (
    <AccordionField
      active
      includesPaths={[
        "metadata.general",
        "metadata.general.title.langstring.lang",
        "metadata.general.title.langstring.#text",
      ]}
      label="Tests"
    >
      <p>0</p>
      <DebugInfo fieldPath="metadata.form" />
      <DebugInfo fieldPath="metadata" />
      <p>1</p>
      <LeftLabeledTextField
        className="twelve wide"
        label="test"
        fieldPath="metadata.general.title.langstring.#text"
        required
      />
      <p>2</p>
      <Form.Field>
        <label htmlFor="metadata.form.test">Test</label>
        <Form.Dropdown
          className="sixteen wide"
          defaultValue=""
          fluid
          id="metadata.form.test"
          name="metadata.form.test"
          options={[
            { key: "1", value: "1", text: "1st" },
            { key: "2", value: "2", text: "2nd" },
          ]}
          placeholder="choose"
          search
          selection
        />
      </Form.Field>
      <p>3</p>
    </AccordionField>
  );
}
