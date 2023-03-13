// This file is part of invenio-records-lom
// Copyright (C) 2022 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { createRef } from "react";
import {
  AccessRightField,
  DeleteButton,
  DepositFormApp,
  DepositStatusBox,
  FileUploader,
  FormFeedback,
  PreviewButton,
  PublishButton,
  SaveButton,
} from "react-invenio-deposit";
import { AccordionField } from "react-invenio-forms";
import { Card, Container, Grid, Ref, Sticky } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

import {
  OptionalAccordion,
  RequiredAccordion,
  TestAccordion,
} from "./components";
import { DebugApiClient } from "./debug";
import { LOMDepositRecordSerializer } from "./serializers";

export default class LOMDepositForm extends React.Component {
  constructor(props) {
    super(props);
    this.config = props.config || {};

    // check if files are present
    this.noFiles = false;
    if (
      !Array.isArray(this.props.files.entries) ||
      (!this.props.files.entries.length && this.props.record.is_published)
    ) {
      this.noFiles = true;
    }
  }

  sidebarRef = createRef();

  render() {
    const recordSerializer = new LOMDepositRecordSerializer(
      this.config.current_locale || this.config.default_locale,
      this.config.vocabularies
    );
    return (
      <DepositFormApp
        config={this.config}
        files={this.props.files}
        permissions={undefined}
        preselectedCommunity={undefined}
        record={this.props.record}
        // below arguments overwrite default-behavior
        apiClient={
          new DebugApiClient(this.props.config.createUrl, recordSerializer)
        }
        recordSerializer={recordSerializer}
        // apiClient={new LOMDepositApiClient()}  // defaults to RDM
        // fileApiClient={new LOMDepositFileApiClient()}  // defaults to RDMDepositFileApiClient
        // draftsService={new LOMDepositDraftsService()}  // defaults to RDMDepositDraftsService, which defers to apiClient
        // filesService={new LOMDepositFilesService()}  // defaults to RDMDeposiFilesService, which defers to fileApiClient
      >
        <FormFeedback
          fieldPath="message"
          labels={{
            "metadata.general": "General",
            "metadata.general.title.langstring.lang": "Title-lang",
          }}
        />
        {/* TODO: Community-Header */}
        <Container id="deposit-form" className="rel-mt-1">
          <Grid className="mt-25">
            <Grid.Column mobile={16} tablet={16} computer={11}>
              <AccordionField
                active
                includesPaths={["files.enabled"]}
                label={i18next.t("Files")}
              >
                {this.noFiles && this.props.record.is_published && (
                  <div className="text-align-center pb-10">
                    <em>{i18next.t("The record has no files.")}</em>
                  </div>
                )}
                <FileUploader
                  isDraftRecord={!this.props.record.is_published}
                  quota={this.config.quota}
                  decimalSizeDisplay={this.config.decimal_size_display}
                />
              </AccordionField>
              <RequiredAccordion />
              <OptionalAccordion />
              {/*<TestAccordion />*/}
            </Grid.Column>
            <Ref innerRef={this.sidebarRef}>
              <Grid.Column
                mobile={16}
                tablet={16}
                computer={5}
                className="deposit-sidebar"
              >
                <Sticky context={this.sidebarRef} offset={20}>
                  <Card>
                    <Card.Content>
                      <DepositStatusBox />
                    </Card.Content>
                    <Card.Content>
                      <Grid relaxed>
                        <Grid.Column
                          computer={8}
                          mobile={16}
                          className="pb-0 left-btn-col"
                        >
                          <SaveButton fluid />
                        </Grid.Column>

                        <Grid.Column
                          computer={8}
                          mobile={16}
                          className="pb-0 right-btn-col"
                        >
                          <PreviewButton fluid />
                        </Grid.Column>

                        <Grid.Column width={16} className="pt-10">
                          <PublishButton fluid />
                        </Grid.Column>
                      </Grid>
                    </Card.Content>
                  </Card>
                  <AccessRightField
                    label={i18next.t("Visibility")}
                    labelIcon="shield"
                    fieldPath="access"
                  />
                  <Card>
                    <Card.Content>
                      <DeleteButton
                        fluid
                        isPublished={this.props.record.is_published}
                      />
                    </Card.Content>
                  </Card>
                </Sticky>
              </Grid.Column>
            </Ref>
          </Grid>
        </Container>
      </DepositFormApp>
    );
  }
}
