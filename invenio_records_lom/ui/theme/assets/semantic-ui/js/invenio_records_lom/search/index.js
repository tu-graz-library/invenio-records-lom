// This file is part of Invenio.
//
// Copyright (C) 2022 Graz University of Technology.
//
// invenio-records-lom is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.

import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  RDMBucketAggregationElement,
  RDMRecordFacets,
  RDMRecordFacetsValues,
  RDMRecordSearchBarContainer,
  RDMRecordMultipleSearchBarElement,
  RDMToggleComponent,
  RDMCountComponent,
} from "@js/invenio_app_rdm/search/components";
import {
  LOMRecordResultsGridItem,
  LOMRecordResultsListItem,
} from "./components";

const initSearchApp = createSearchAppInit({
  "BucketAggregation.element": RDMBucketAggregationElement,
  "BucketAggregationValues.element": RDMRecordFacetsValues,
  "ResultsGrid.item": LOMRecordResultsGridItem,
  "ResultsList.item": LOMRecordResultsListItem,
  "SearchApp.facets": RDMRecordFacets,
  "SearchApp.searchbarContainer": RDMRecordSearchBarContainer,
  "SearchBar.element": RDMRecordMultipleSearchBarElement,
  "SearchFilters.ToggleComponent": RDMToggleComponent,
  "Count.element": RDMCountComponent,
});
