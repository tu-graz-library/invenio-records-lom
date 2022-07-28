// This file is part of Invenio.
//
// Copyright (C) 2022 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import React, { useState } from "react";
import ReactDOM from "react-dom";
import { get, camelCase, truncate } from "lodash";
import {
  Button,
  Card,
  Checkbox,
  Icon,
  Input,
  Item,
  Label,
  List,
} from "semantic-ui-react";
import { BucketAggregation } from "react-searchkit";
import { loadComponents } from "@js/invenio_theme/templates";
import Overridable from "react-overridable";
import { SearchBar, SearchApp } from "@js/invenio_search_ui/components";

export const LOMRecordResultsListItem = ({ result, index }) => {
  const ui = get(result, "ui", {});
  const access = get(ui, "access_status", {});

  const createdDate = get(
    ui,
    "created_date_l10n_long",
    "No creation date found."
  );

  const publicationDate = get(
    ui,
    "created_date_l10n_long",
    "No update date found."
  );

  const access_id = get(access, "id", "Public");
  const access_status = get(access, "title", "Public");
  const access_icon = get(access, "icon", "unlock");

  const description = get(ui, "generalDescriptions", "No description");

  const persons = get(ui, "contributors", []);

  const title = get(ui, "title", "No title");
  const version = get(result, "metadata.lifecycle.version", null);

  const subjects = [];

  const viewLink = `/lom/${result.id}`;

  return (
    <Item key={index}>
      <Item.Content>
        <Item.Extra>
          <div>
            <Label size="tiny" color="blue">
              {publicationDate} {version ? `(${version})` : null}
            </Label>
            <Label size="tiny" className={`access-status ${access_id}`}>
              {access_icon && <i className={`icon ${access_icon}`}></i>}
              {access_status}
            </Label>
          </div>
        </Item.Extra>
        <Item.Header as="h2">
          <a href={viewLink}>{title}</a>
        </Item.Header>
        <Item.Meta>
          {persons.map((person, index) => (
            <span key={index}>
              {person.fullname}
              {index < persons.length - 1 && ","}
            </span>
          ))}
        </Item.Meta>
        <Item.Description>
          {truncate(description, { length: 350 })}
        </Item.Description>
        <Item.Extra>
          {subjects.map((subject, index) => (
            <Label key={index} size="tiny">
              {subject.miscellaneous_information}
            </Label>
          ))}
          {createdDate && (
            <div>
              <small>
                Uploaded on <span>{createdDate}</span>
              </small>
            </div>
          )}
        </Item.Extra>
      </Item.Content>
    </Item>
  );
};

export const LOMRecordResultsGridItem = ({ result, index }) => {
  const metadata = get(result, ["ui", "metadata", "json"], []);
  const description = get(
    metadata,
    ["summary", "0", "summary"],
    "No description"
  );
  return (
    <Card fluid key={index} href={`/lom/${result.pid}`}>
      <Card.Content>
        <Card.Header>{result.metadata.json.title_statement.title}</Card.Header>
        <Card.Description>
          {truncate(description, { length: 200 })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
};
