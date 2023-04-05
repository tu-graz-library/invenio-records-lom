// This file is part of Invenio
// Copyright (C) 2022 Graz University of Technology.
//
// React-Invenio-Deposit is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Field as FormikField, getIn, useFormikContext } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React, { useEffect } from "react";
import { GroupField } from "react-invenio-forms";
import { useSelector } from "react-redux";
import { Button, Dropdown, Form, Icon, Label } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

// TODO: htmlFor on <label>s and <FieldLabel>s
//       className="field-label-class invenio-field-label" for <label>s
// TODO: i18next.t
// TODO: prop-types

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

const FieldLabel = ({ fieldPath, iconName, label, required }) => {
  const icon = iconName ? <Icon name={iconName} /> : null;
  const requiredIcon = required ? <Icon color="red" name="asterisk" /> : null;
  return label || icon ? (
    <label htmlFor={fieldPath || null}>
      {requiredIcon}
      {icon}
      {label}
    </label>
  ) : null;
};

export class LeftLabeledTextField extends React.Component {
  renderFormField = (formikBag) => {
    let { className, debug, fieldPath, label, placeholder, required, rows } =
      this.props;
    const {
      form: {
        errors,
        handleChange,
        handleBlur,
        initialErrors,
        isSubmitting,
        values,
      },
    } = formikBag;
    const error =
      getIn(errors, fieldPath, null) || getIn(initialErrors, fieldPath, null);
    rows = rows && Number(rows);
    const InputTag = rows && rows > 1 ? "textarea" : "input";
    return (
      <Form.Field
        error={error}
        className={className}
        id={fieldPath}
        required={required}
      >
        <div className="ui labeled input">
          {label && (
            <div className={`ui label${error ? " error" : ""}`}>{label}</div>
          )}
          <InputTag
            disabled={isSubmitting}
            fluid="true"
            id={fieldPath}
            label={label}
            name={fieldPath}
            onBlur={handleBlur}
            onChange={handleChange}
            placeholder={placeholder}
            rows={rows}
            type="text"
            value={getIn(values, fieldPath, "")}
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

  render() {
    const { fieldPath } = this.props;
    return <FormikField component={this.renderFormField} name={fieldPath} />;
  }
}

export const TitledTextField = (props) => {
  const {
    closeAction,
    debug,
    fieldPath,
    iconName,
    label,
    placeholder,
    required,
    rows,
    title,
  } = props;
  const icon = iconName ? <Icon name={iconName} /> : null;
  const requiredIcon = required ? <Icon color="red" name="asterisk" /> : null;
  const labelElement =
    title || icon ? (
      <label htmlFor={fieldPath}>
        {requiredIcon}
        {icon}
        {title}
      </label>
    ) : null;

  return (
    <div className="field">
      {labelElement}
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

export class DropdownField extends React.Component {
  renderFormField = (formikBag) => {
    const {
      closeAction,
      debug,
      fieldPath,
      iconName,
      placeholder,
      required,
      title,
      vocabularyName,
    } = this.props;
    const {
      form: {
        errors,
        handleBlur,
        intitalErrors,
        isSubmitting,
        setFieldValue,
        values,
      },
    } = formikBag;
    const vocabulary = useSelector((state) =>
      _get(state, `deposit.config.vocabularies.${vocabularyName}`, {})
    );
    const error =
      getIn(errors, fieldPath, null) || getIn(intitalErrors, fieldPath, null);

    // `vocabulary` is {1: {name: "NATURAL SCIENCES"}, 101: {name: "Mathematics"}, ...}
    // Form.Dropdown needs [{key: "1", value: "1", text: "1 - NATURAL SCIENCES"}, ...]
    const options = Object.entries(vocabulary).map(([key, { name }]) => ({
      key,
      value: key,
      text: name,
    }));
    options.sort((lhs, rhs) => String(lhs.key).localeCompare(rhs.key));

    return (
      <Form.Field>
        <FieldLabel iconName={iconName} label={title} required={required} />
        <GroupField fieldPath={fieldPath}>
          <Form.Dropdown
            className="sixteen wide"
            defaultValue={getIn(values, `${fieldPath}.value`, null)}
            disabled={isSubmitting}
            error={error}
            fluid
            id={fieldPath}
            name={fieldPath}
            onBlur={handleBlur}
            onChange={(e, { name, value }) =>
              setFieldValue(`${name}.value`, value)
            }
            options={options}
            placeholder={placeholder}
            search
            selection
          />
          <CloseButton closeAction={closeAction} />
        </GroupField>
        {debug && <DebugInfo fieldPath={fieldPath} />}
      </Form.Field>
    );
  };
  render() {
    const { fieldPath } = this.props;
    return <FormikField component={this.renderFormField} name={fieldPath} />;
  }
}

export class ContributorField extends React.Component {
  renderFormField = (formikBag) => {
    const { closeAction, fieldPath, vocabularyName } = this.props;
    const {
      form: { handleBlur, isSubmitting, setFieldValue, values },
    } = formikBag;
    const vocabulary = useSelector((state) =>
      _get(state, `deposit.config.vocabularies.${vocabularyName}`, {})
    );

    const options = Object.entries(vocabulary).map(([key, { name }]) => ({
      key,
      value: key,
      text: name,
    }));
    return (
      <Form.Field>
        <GroupField fieldPath={fieldPath}>
          <Form.Dropdown
            className="four wide"
            defaultValue={getIn(values, `${fieldPath}.role.value`, null)}
            disabled={isSubmitting}
            fluid
            id={`${fieldPath}.role`}
            name={`${fieldPath}.role`}
            onBlur={handleBlur}
            onChange={(e, { name, value }) =>
              setFieldValue(`${name}.value`, value)
            }
            options={options}
            placeholder={i18next.t("Select Role")}
            search
            selection
          />
          <LeftLabeledTextField
            className="twelve wide"
            fieldPath={`${fieldPath}.name`}
            label={i18next.t("Name")}
            placeholder={i18next.t("Enter name here")}
          />
          <CloseButton closeAction={closeAction} />
        </GroupField>
      </Form.Field>
    );
  };
  render() {
    const { fieldPath } = this.props;
    return <FormikField component={this.renderFormField} name={fieldPath} />;
  }
}

export const LangstringGroupField = (props) => {
  const {
    closeAction,
    debug,
    fieldPath,
    iconName,
    label,
    placeholder,
    required,
    rows,
    title,
  } = props;
  const icon = iconName ? <Icon name={iconName} /> : null;
  const requiredIcon = required ? <Icon color="red" name="asterisk" /> : null;
  const labelElement =
    title || icon ? (
      <label htmlFor={`${fieldPath}.langstring.#text`}>
        {requiredIcon}
        {icon}
        {title}
      </label>
    ) : null;

  return (
    <div className="field">
      {labelElement}
      <GroupField fieldPath={fieldPath}>
        <LeftLabeledTextField
          className="twelve wide"
          debug={debug}
          fieldPath={`${fieldPath}.langstring.#text`}
          label={label}
          placeholder={placeholder}
          required={required}
          rows={rows}
        />
        <LeftLabeledTextField
          className="four wide"
          debug={debug}
          fieldPath={`${fieldPath}.langstring.lang`}
          label="Language"
          placeholder="e.g. en, de"
          required={required}
        />
        <CloseButton closeAction={closeAction} />
      </GroupField>
      {debug && <DebugInfo fieldPath={fieldPath} />}
    </div>
  );
};

export const LangstringSingleField = (props) => {
  const {
    closeAction,
    debug,
    fieldPath,
    iconName,
    label,
    placeholder,
    required,
    rows,
    title,
  } = props;
  const icon = iconName ? <Icon name={iconName} /> : null;
  const requiredIcon = required ? <Icon color="red" name="asterisk" /> : null;
  const labelElement =
    title || icon ? (
      <label htmlFor={`${fieldPath}.langstring.#text`}>
        {requiredIcon}
        {icon}
        {title}
      </label>
    ) : null;

  return (
    <div className="field">
      {labelElement}
      <GroupField fieldPath={fieldPath}>
        <LeftLabeledTextField
          className="sixteen wide"
          debug={debug}
          fieldPath={`${fieldPath}.langstring.#text`}
          label={label}
          placeholder={placeholder}
          required={required}
          rows={rows}
        />
        <CloseButton closeAction={closeAction} />
      </GroupField>
      {debug && <DebugInfo fieldPath={fieldPath} />}
    </div>
  );
};

export class VocabularyGroupField extends React.Component {
  render() {
    const {
      closeAction,
      debug,
      fieldPath,
      icon,
      label,
      placeholder,
      required,
      title,
    } = this.props;

    const requiredIcon = required ? <Icon color="red" name="asterisk" /> : null;
    const labelElement =
      title || icon ? (
        <label>
          {requiredIcon}
          {icon}
          {title}
        </label>
      ) : null;

    return (
      <div className="field">
        {labelElement}
        <GroupField fieldPath={fieldPath}>
          <LeftLabeledTextField
            className="twelve wide"
            debug={debug}
            fieldPath={`${fieldPath}.entry.langstring.#text`}
            label={label}
            placeholder={placeholder}
            required={required}
          />
          <LeftLabeledTextField
            className="four wide"
            debug={debug}
            fieldPath={`${fieldPath}.catalog`}
            label="Catalog"
            placeholder='e.g. "ISBN", "DOI"'
            required={required}
          />
          <CloseButton closeAction={closeAction} />
        </GroupField>
        {debug && <DebugInfo fieldPath={fieldPath} />}
      </div>
    );
  }
}
