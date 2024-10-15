// Copyright (C) 2022-2024 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { EditButton } from "@js/invenio_records_lom/components/EditButton";
import { get, truncate } from "lodash";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Card, Icon, Item, Label, Popup } from "semantic-ui-react";

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

LOMBucketAggregationElement.propTypes = {
  containerCmp: PropTypes.node,
  title: PropTypes.node.isRequired,
};

LOMBucketAggregationElement.defaultProps = {
  containerCmp: null,
};

export const LomStats = ({ uniqueViews, uniqueDownloads }) => {
  return (
    <>
      {uniqueViews != null && (
        <Popup
          size="tiny"
          content="Views"
          trigger={
            <Label className="transparent">
              <Icon name="eye" />
              {uniqueViews}
            </Label>
          }
        />
      )}
      {uniqueDownloads != null && (
        <Popup
          size="tiny"
          content="Downloads"
          trigger={
            <Label className="transparent">
              <Icon name="download" />
              {uniqueDownloads}
            </Label>
          }
        />
      )}
    </>
  );
};

LomStats.propTypes = {
  uniqueViews: PropTypes.number,
  uniqueDownloads: PropTypes.number,
};

LomStats.defaultProps = {
  uniqueViews: null,
  uniqueDownloads: null,
};

export const LOMRecordResultsListItem = ({ result, index }) => {
  const ui = get(result, "ui", {});
  const access = get(ui, "access_status", {});

  const createdDate = get(ui, "created_date_l10n_long", "No creation date found.");

  const publicationDate = get(ui, "created_date_l10n_long", "No update date found.");

  const accessId = get(access, "id", "Public");
  const accessStatus = get(access, "title", "Public");
  const accessIcon = get(access, "icon", "unlock");

  const description = get(ui, "generalDescriptions", "No description");

  const persons = get(ui, "contributors", []);

  const title = get(ui, "title", "No title");
  const version = get(result, "metadata.lifecycle.version.langstring.#text", null);

  const uniqueViews = get(result, "stats.all_versions.unique_views", 0);
  const uniqueDownloads = get(result, "stats.all_versions.unique_downloads", 0);

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
            <Label size="tiny" className={`access-status ${accessId}`}>
              {accessIcon && <i className={`icon ${accessIcon}`} />}
              {accessStatus}
            </Label>
            <div className="ui right floated">
              <EditButton
                recid={result.id}
                onError={handleError}
                compact
                floated="right"
                size="small"
              />
              {error && (
                <Label basic color="red" pointing="right">
                  {error}
                </Label>
              )}
            </div>
          </div>
        </Item.Extra>
        <Item.Header as="h2">
          <a href={viewLink}>{title}</a>
        </Item.Header>
        <Item.Meta>
          {persons.map((person, index) => (
            <span key={`${person.role}:${person.fullname}`}>
              {person.fullname}
              {index < persons.length - 1 && ","}
            </span>
          ))}
        </Item.Meta>
        <Item.Description>{truncate(description, { length: 350 })}</Item.Description>
        <Item.Extra>
          <div className="flex justify-space-between align-items-end">
            {createdDate && (
              <small>
                Uploaded on <span>{createdDate}</span>
              </small>
            )}
            <small>
              <LomStats uniqueViews={uniqueViews} uniqueDownloads={uniqueDownloads} />
            </small>
          </div>
        </Item.Extra>
      </Item.Content>
    </Item>
  );
};

LOMRecordResultsListItem.propTypes = {
  index: PropTypes.any,
  result: PropTypes.object.isRequired,
};

LOMRecordResultsListItem.defaultProps = {
  index: null,
};

export const LOMRecordResultsGridItem = ({ result, index }) => {
  const metadata = get(result, ["ui", "metadata", "json"], []);
  const description = get(metadata, ["summary", "0", "summary"], "No description");
  return (
    <Card fluid key={index} href={`/oer/${result.pid}`}>
      <Card.Content>
        <Card.Header>{result.metadata.json.title_statement.title}</Card.Header>
        <Card.Description>{truncate(description, { length: 200 })}</Card.Description>
      </Card.Content>
    </Card>
  );
};

LOMRecordResultsGridItem.propTypes = {
  index: PropTypes.any,
  result: PropTypes.object.isRequired,
};

LOMRecordResultsGridItem.defaultProps = {
  index: null,
};
