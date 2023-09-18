// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { getIn, useField, useFormikContext } from "formik";
import _get from "lodash/get";
import React from "react";
import { GroupField } from "react-invenio-forms";
import { useSelector } from "react-redux";
import { Button, Form, Icon, Label } from "semantic-ui-react";
import { i18next } from "@translations/invenio_records_lom/i18next";

// TODO: consider changing invenio `GroupField`s for `Form.Group`
// TODO: move id for author/publisher from contributor.1 to contributor.1.something
//       - errors can't be applied to both it (requires error[contributor.1] is string)
//         and name (requires error[contributor.1] = {name: String}) otherwise...
//       - add errors to field while at it...
// TODO: data within [...] needs be objects to be handled correctly by invenio's `ArrayField`s
//       tags achieve this by setting fieldPath to `path.{index}.value`
//       DropdownField implicitly adds `.value` internally
//         ~> look into whether {value: String} vs String is really necessary
// TODO: validationSchema for instant error-feedback
// TODO: prop-types and/or doc-strings
//       doc-string: put above function:
//           /**
//             * General function description.
//             *
//             * @param {Object} props
//             * @param {String} props.subValue - Description of param
//             * @returns
//             */
//       prop-types: put below React-function:
//           ReactComp.propTypes = {
//             fieldPath: PropTypes.string.isrequired,
//             label: PropTypes.oneOfType(PropTypes.string, PropTypes.node),
//           }
// TODO: some fields aren't disabled while submitting...
// TODO: translations are registered by i18n, but not yet done
// TODO: fix includesPaths of `ArrayField`s
// TODO: stop using DebugAPIClient

export const DebugInfo = ({ fieldPath }) => {
  const { values } = useFormikContext();
  return (
    <div style={{ whiteSpace: "pre", fontFamily: "monospace" }}>
      {JSON.stringify(getIn(values, fieldPath), null, 2)}
    </div>
  );
};

const CloseButton = ({ closeAction }) => {
  return closeAction ? (
    <Form.Field>
      <Button
        aria-label={i18next.t("Remove Field")}
        className="close-btn"
        icon="close"
        onClick={closeAction}
      />
    </Form.Field>
  ) : null;
};

const FieldLabel = ({ htmlFor, iconName, label, required }) => {
  const icon = iconName ? <Icon name={iconName} /> : null;
  const requiredIcon = required ? <Icon color="red" name="asterisk" /> : null;
  return label || icon ? (
    <label
      className="field-label-class invenio-field-label"
      htmlFor={htmlFor || null}
    >
      {requiredIcon}
      {icon}
      {label}
    </label>
  ) : null;
};

export const LeftLabeledTextField = ({
  className,
  debug,
  fieldPath,
  label,
  placeholder,
  required,
  rows,
}) => {
  // register field and get field-specific formik-context
  // NOTE: in function react-components this needs be called for its internal
  //       useEffect, which registers the field with formik
  const [fieldProps, fieldMeta] = useField(fieldPath);

  // get general formik-context shared by all fields
  const { isSubmitting } = useFormikContext();

  const error = fieldMeta.error || fieldMeta.initialError || null;
  rows = rows && Number(rows);
  const InputTag = rows && rows > 1 ? "textarea" : "input";

  return (
    <Form.Field error={error} className={className} required={required}>
      <div className="ui labeled input">
        {label && (
          <label
            className={`ui label${error ? " error" : ""}`}
            htmlFor={fieldPath}
          >
            {label}
          </label>
        )}
        <InputTag
          disabled={isSubmitting}
          fluid="true"
          id={fieldPath}
          label={label}
          name={fieldPath}
          onBlur={fieldProps.onBlur}
          onChange={fieldProps.onChange}
          placeholder={placeholder}
          rows={rows}
          type="text"
          value={fieldMeta.value}
        />
        {required && (
          <div className="ui corner label">
            <i className="red asterisk icon" />
          </div>
        )}
      </div>
      {error && (
        <Label pointing prompt>
          {error}
        </Label>
      )}
      {debug && <DebugInfo fieldPath={fieldPath} />}
    </Form.Field>
  );
};

export const TitledTextField = ({
  closeAction,
  debug,
  fieldPath,
  iconName,
  label,
  placeholder,
  required,
  rows,
  title,
}) => {
  return (
    <div className="field">
      <FieldLabel
        htmlFor={fieldPath}
        iconName={iconName}
        label={title}
        required={required}
      />
      <GroupField fieldPath={fieldPath}>
        <LeftLabeledTextField
          className="sixteen wide"
          debug={debug}
          fieldPath={fieldPath}
          label={label}
          placeholder={placeholder}
          rows={rows}
        />
        <CloseButton closeAction={closeAction} />
      </GroupField>
      {debug && <DebugInfo fieldPath={fieldPath} />}
    </div>
  );
};

const InnerDropdownField = ({
  className,
  clearable,
  fieldPath,
  placeholder,
  vocabularyName,
}) => {
  // register field and get field-specific formik-context
  // NOTE: in function react-components this needs be called for its internal
  //       useEffect, which registers the field with formik
  const [fieldProps, fieldMeta, fieldHelpers] = useField(`${fieldPath}.value`);

  // get general formik-context shared by all fields
  const { isSubmitting } = useFormikContext();

  // get associated vocabulary from redux
  const vocabulary = useSelector((state) =>
    _get(state, `deposit.config.vocabularies.${vocabularyName}`, {})
  );

  const error = fieldMeta.error || fieldMeta.initialError || null;
  // `vocabulary` is {1: {name: "NATURAL SCIENCES"}, 101: {name: "Mathematics"}, ...}
  // Dropdown needs [{key: "1", value: "1", text: "NATURAL SCIENCES"}, ...]
  const options = Object.entries(vocabulary).map(([key, { name }]) => ({
    key,
    value: key,
    text: name,
  }));
  options.sort((lhs, rhs) => String(lhs.key).localeCompare(rhs.key));

  return (
    // For correct placement within a web-form, `Form.Dropdown` is used here,
    // which differs from `Dropdown` in that it's wrapped in an additional <div class="field" />
    <Form.Dropdown
      className={className || "sixteen wide"}
      clearable={clearable}
      defaultValue={fieldMeta.value || null}
      disabled={isSubmitting}
      error={error}
      fluid
      name={fieldPath}
      noResultsMessage={i18next.t("No results found.")}
      onBlur={fieldProps.onBlur}
      onChange={(e, { value }) => fieldHelpers.setValue(value)}
      options={options}
      placeholder={placeholder}
      search
      searchInput={{ id: fieldPath }}
      selection
      value={fieldMeta.value || null}
    />
  );
};

export const DropdownField = ({
  clearable,
  closeAction,
  debug,
  fieldPath,
  iconName,
  placeholder,
  required,
  title,
  vocabularyName,
}) => {
  return (
    <Form.Field>
      <FieldLabel
        htmlFor={fieldPath}
        iconName={iconName}
        label={title}
        required={required}
      />
      <GroupField fieldPath={fieldPath}>
        <InnerDropdownField
          clearable={clearable}
          fieldPath={fieldPath}
          placeholder={placeholder}
          vocabularyName={vocabularyName}
        />
        <CloseButton closeAction={closeAction} />
      </GroupField>
      {debug && <DebugInfo fieldPath={fieldPath} />}
    </Form.Field>
  );
};

export const ContributorField = ({
  closeAction,
  debug,
  fieldPath,
  vocabularyName,
}) => {
  return (
    <Form.Field>
      <GroupField fieldPath={fieldPath}>
        <InnerDropdownField
          className={"four wide"}
          fieldPath={`${fieldPath}.role`}
          placeholder={i18next.t("Select role")}
          vocabularyName={vocabularyName}
        />
        <LeftLabeledTextField
          className="twelve wide"
          debug={debug}
          fieldPath={`${fieldPath}.name`}
          label={i18next.t("Name")}
          placeholder={i18next.t("Enter name here")}
        />
        <CloseButton closeAction={closeAction} />
      </GroupField>
      {debug && <DebugInfo fieldPath={fieldPath} />}
    </Form.Field>
  );
};
