// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import { get, truncate } from "lodash";
import { Card, Icon, Item, Label } from "semantic-ui-react";
import { EditButton } from "@js/invenio_records_lom/components/EditButton";

export const LOMBucketAggregationElement = ({ title, containerCmp }) => {
  const [active, setActive] = useState(true);

  return (
    <Card className="borderless facet">
      <Card.Content>
        <Card.Header
          as="h2"
          style={{ float: "left", minHeight: 0, cursor: "pointer" }}
          onClick={() => setActive((active) => !active)}
        >
          <Icon
            style={{ "margin-top": "-4px" }}
            name={active ? "angle down" : "angle right"}
          />
          {title}
        </Card.Header>
        {active ? containerCmp : null}
      </Card.Content>
    </Card>
  );
};

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
  const version = get(
    result,
    "metadata.lifecycle.version.langstring.#text",
    null
  );

  const subjects = [];

  const viewLink = `/oer/${result.id}`;

  const [error, setError] = useState("");
  const handleError = (errorMessage) => {
    setError(errorMessage);
  };

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
            <EditButton recid={result.id} onError={handleError} />
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
    <Card fluid key={index} href={`/oer/${result.pid}`}>
      <Card.Content>
        <Card.Header>{result.metadata.json.title_statement.title}</Card.Header>
        <Card.Description>
          {truncate(description, { length: 200 })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
};
