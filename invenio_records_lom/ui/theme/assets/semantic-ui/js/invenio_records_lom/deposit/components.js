// This file is part of invenio-records-lom
// Copyright (C) 2022 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Field as FormikField } from "formik";
import React from "react";
import {
  AccordionField,
  ArrayField,
  FieldLabel,
  GroupField,
  RichInputField,
  TextField,
} from "react-invenio-forms";
import { Button, Divider, Form, Icon, Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

import {
  ContributorField,
  DebugInfo,
  LangstringGroupField,
  LeftLabeledTextField,
  DropdownField,
  TitledTextField,
  VocabularyGroupField,
} from "./fields";

// TODO: translations via i18next.t

export function RequiredAccordion(props) {
  return (
    <AccordionField
      active
      includesPaths={[
        "metadata.general",
        "metadata.general.title.langstring.lang",
        "metadata.general.title.langstring.#text",
      ]}
      label="Required Fields"
    >
      <TitledTextField
        fieldPath="metadata.form.title"
        label="Title"
        placeholder="Enter your title here."
        required
      />
      <DropdownField
        fieldPath="metadata.form.license"
        iconName="drivers license"
        placeholder="Select License"
        required
        title="License"
        vocabularyName="license"
      />
      <ArrayField
        addButtonLabel="Add Contributor"
        defaultNewValue={{}}
        fieldPath="metadata.form.contributor"
        label={
          <label>
            <Icon name="red asterisk" />
            <Icon name="user plus" />
            {"Contributors"}
          </label>
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
        addButtonLabel="Add OEFOS"
        defaultNewValue={{}}
        fieldPath="metadata.form.oefos"
        label={
          //<FieldLabel icon="barcode" label="OEFOS" />
          <label>
            <Icon name="red asterisk" />
            <Icon name="barcode" />
            {"OEFOS"}
          </label>
        }
      >
        {({ arrayHelpers, indexPath }) => (
          <DropdownField
            closeAction={() => arrayHelpers.remove(indexPath)}
            fieldPath={`metadata.form.oefos.${indexPath}`}
            placeholder="Select OEFOS"
            vocabularyName="oefos"
          />
        )}
      </ArrayField>
    </AccordionField>
  );
}

export function OptionalAccordion(props) {
  return (
    <AccordionField includesPaths={[]} label="Optional">
      <TitledTextField
        fieldPath="metadata.form.description"
        label="Description"
        placeholder="Enter your description here."
        rows={5}
      />
      <ArrayField
        addButtonLabel="Add Tag"
        defaultNewValue={{ value: "" }}
        fieldPath="metadata.form.tag"
        label={<FieldLabel icon="tag" label="Tags" />}
      >
        {({ arrayHelpers, indexPath }) => (
          <TitledTextField
            closeAction={() => arrayHelpers.remove(indexPath)}
            fieldPath={`metadata.form.tag.${indexPath}.value`}
            label="Tag"
            placeholder="Enter your tag here"
          />
        )}
      </ArrayField>
      <DropdownField
        fieldPath="metadata.form.language"
        iconName="globe"
        placeholder="Select Language"
        title="Language"
        vocabularyName="language"
      />
      {
        // TODO: resource_type
      }
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
      label={"Tests"}
    >
      <DebugInfo fieldPath="metadata" />
      <p>1</p>
      <LeftLabeledTextField
        className="twelve wide"
        label="test"
        fieldPath="metadata.general.title.langstring.#text"
        required
      />
      <p>2</p>
      <LangstringGroupField
        debug
        fieldPath="metadata.general.title"
        label="Test"
        placeholder="Hitchhiker's Guide to the Galaxy"
      />
      <p>3</p>
      <LangstringGroupField
        fieldPath="metadata.general.title"
        iconName="book"
        label="label"
        placeholder="Hitchhiker's Guide to the Galaxy"
        required
        title="Title"
      />
      <p>4</p>
      <ArrayField
        addButtonLabel="Add Description"
        defaultNewValue={{ langstring: { "#text": "", lang: "" } }}
        fieldPath="metadata.general.description"
        label={
          <FieldLabel
            htmlfor="metadata.general.description"
            icon="pencil"
            label="Descriptions"
          />
        }
      >
        {({ arrayHelpers, indexPath }) => (
          <LangstringGroupField
            debug
            closeAction={() => arrayHelpers.remove(indexPath)}
            fieldPath={`metadata.general.description.${indexPath}`}
            label="Description"
            rows="5"
          />
        )}
      </ArrayField>
      <p>5</p>
      <LangstringGroupField />
      <p>6</p>
      <DebugInfo fieldPath="metadata.general.identifier" />
      <ArrayField
        addButtonLabel="Add Identifier"
        defaultNewValue={{
          catalog: "",
          entry: { langstring: { "#text": "", lang: "x-none" } },
        }}
        fieldPath="metadata.general.identifier"
        label={
          <FieldLabel
            htmlFor="metadata.general.identifier"
            icon="barcode"
            label="Identifiers"
          />
        }
      >
        {({ arrayHelpers, indexPath }) => (
          <VocabularyGroupField
            closeAction={() => arrayHelpers.remove(indexPath)}
            debug
            fieldPath={`metadata.general.identifier.${indexPath}`}
            label="Identifier"
            placeholder="e.g. 123456-789"
          />
        )}
      </ArrayField>
      <p>7</p>
      <ArrayField
        addButtonLabel="Add OEFOS"
        defaultNewValue={{}}
        fieldPath="metadata.oefos"
        label={<FieldLabel icon="barcode" label="OEFOS" />}
      >
        {({ arrayHelpers, indexPath }) => (
          <DropdownField
            closeAction={() => arrayHelpers.remove(indexPath)}
            debug
            fieldPath={`metadata.oefos.${indexPath}`}
          />
        )}
      </ArrayField>
      <DebugInfo fieldPath="metadata.oefos" />
      <p>8</p>
    </AccordionField>
  );
}

const Language = () => {
  return (
    <ArrayField
      addButtonLabel="Add Language"
      defaultNewValue={{ value: "" }}
      fieldPath="metadata.general.language"
      label={
        <FieldLabel
          htmlFor="metadata.general.language"
          icon="globe"
          label="Languages"
        />
      }
    >
      {({ arrayHelpers, indexPath }) => (
        <GroupField>
          <TextField
            fieldPath={`metadata.general.language.${indexPath}.value`}
            helpText={null}
            label={null}
            placeholder=""
            width={16}
          />
          <Form.Field>
            <Button
              aria-label="Remove Field"
              className="close-btn"
              icon="close"
              onClick={() => arrayHelpers.remove(indexPath)}
            />
          </Form.Field>
        </GroupField>
      )}
    </ArrayField>
  );
};

const RichInput = ({ indexPath }) => {
  return (
    <RichInputField
      className="fourteen wide"
      fieldPath={`metadata.general.description.${indexPath}.langstring.#text`}
      editorConfig={{
        removePlugins: [
          "Image",
          "ImageCaption",
          "ImageStyle",
          "ImageToolbar",
          "ImageUpload",
          "MediaEmbed",
          "Table",
          "TableToolbar",
          "TableProperties",
          "TableCellProperties",
        ],
      }}
      label={
        <FieldLabel
          htmlFor={`metadata.general.description.${indexPath}.langstring.#text`}
          icon="pencil"
          label="Description"
        />
      }
      optimized
    />
  );
};
const FormikChildren = ({ indexPath }) => {
  <FormikField
    className="invenio-text-input-field"
    id={`metadata.lifecycle.identifier.${indexPath}.catalog`}
    name={`metadata.lifecycle.identifier.${indexPath}.catalog`}
  >
    {({ field, meta }) => {
      return (
        <div className="four wide field">
          <Input
            {...field}
            error={meta.error}
            fluid
            label="Catalog"
            placeholder="e.g. ISBN, DOI"
            type="text"
          />
        </div>
      );
    }}
  </FormikField>;
};
