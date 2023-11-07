// This file is part of Invenio.
//
// Copyright (C) 2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify
// it under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { parametrize } from "react-overridable";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { Button, Divider, Header, Segment, Grid } from "semantic-ui-react";
import { SearchBar, Sort } from "react-searchkit";
import {
  RDMRecordSearchBarContainer,
  RDMRecordSearchBarElement,
  RDMToggleComponent,
  RDMCountComponent,
  RDMErrorComponent,
} from "@js/invenio_app_rdm/search/components";
import {
  ContribSearchAppFacets,
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";
import {
  LOMRecordResultsGridItem,
  LOMRecordResultsListItem,
} from "@js/invenio_records_lom/search/components";
import { i18next } from "@translations/invenio_records_lom/i18next";
import {
  DashboardSearchLayoutHOC,
  DashboardResultView,
} from "@js/invenio_app_rdm/user_dashboard/base";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toogle: true,
});

export const LOMSearchLayout = DashboardSearchLayoutHOC({
  searchBarPlaceholder: i18next.t("Search in Open Educational Resources..."),
});

export const LOMEmptyResults = (props) => {
  return (
    <Segment.Group>
      <Segment placeholder textAlign="center" padded="very">
        <Header as="h1" align="center">
          <Header.Content>
            <Header.Subheader>
              {i18next.t("Make your first upload!")}
            </Header.Subheader>
          </Header.Content>
        </Header>
        <Divider hidden />
        <Button
          positive
          icon="upload"
          floated="right"
          href="/oer/uploads/new"
          content={i18next.t("New upload")}
        />
      </Segment>
    </Segment.Group>
  );
};

const initSearchApp = createSearchAppInit({
  "BucketAggregation.element": ContribBucketAggregationElement,
  "BucketAggregationValues.element": ContribBucketAggregationValuesElement,
  "EmptyResults.element": LOMEmptyResults,
  "ResultsGrid.item": LOMRecordResultsGridItem,
  "ResultsList.item": LOMRecordResultsListItem,
  "SearchApp.facets": ContribSearchAppFacetsWithConfig,
  "SearchApp.searchbarContainer": RDMRecordSearchBarContainer,
  "SearchBar.element": RDMRecordSearchBarElement,
  "SearchApp.layout": LOMSearchLayout,
  "SearchApp.results": DashboardResultView,
  "SearchFilters.ToggleComponent": RDMToggleComponent,
  "Error.element": RDMErrorComponent,
  "Count.element": RDMCountComponent,
  "SearchFilters.Toggle.element": RDMToggleComponent,
});
