// Copyright (C) 2022-2023 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { parametrize } from "react-overridable";
import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  RDMRecordSearchBarContainer,
  RDMRecordMultipleSearchBarElement,
  RDMToggleComponent,
  RDMCountComponent,
} from "@js/invenio_app_rdm/search/components";
import {
  ContribSearchAppFacets,
  ContribBucketAggregationValuesElement,
} from "@js/invenio_search_ui/components";
import {
  LOMBucketAggregationElement,
  LOMRecordResultsGridItem,
  LOMRecordResultsListItem,
} from "./components";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toogle: true,
});

const initSearchApp = createSearchAppInit({
  "BucketAggregation.element": LOMBucketAggregationElement,
  "BucketAggregationValues.element": ContribBucketAggregationValuesElement,
  "ResultsGrid.item": LOMRecordResultsGridItem,
  "ResultsList.item": LOMRecordResultsListItem,
  "SearchApp.facets": ContribSearchAppFacetsWithConfig,
  "SearchApp.searchbarContainer": RDMRecordSearchBarContainer,
  "SearchBar.element": RDMRecordMultipleSearchBarElement,
  "SearchFilters.ToggleComponent": RDMToggleComponent,
  "Count.element": RDMCountComponent,
});
