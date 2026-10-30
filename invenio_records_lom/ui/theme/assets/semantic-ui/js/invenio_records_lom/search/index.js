/*
 * SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import {
  RDMCountComponent,
  RDMRecordMultipleSearchBarElement,
  RDMRecordSearchBarContainer,
  RDMToggleComponent,
} from "@js/invenio_app_rdm/search/components";
import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  ContribBucketAggregationValuesElement,
  ContribSearchAppFacets,
} from "@js/invenio_search_ui/components";
import { parametrize } from "react-overridable";
import {
  LOMBucketAggregationElement,
  LOMRecordResultsGridItem,
  LOMRecordResultsListItem,
} from "./components";

const ContribSearchAppFacetsWithConfig = parametrize(ContribSearchAppFacets, {
  toogle: true,
});

// per default, this also initializes the search-app (2nd argument, named `autoInit`)
createSearchAppInit({
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
