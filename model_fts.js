{
  "dataset": {
    "model_rev": 1,
    "name": "ecfts",
    "label": "EC Financial Transparency System", 
    "description": "All grants and commitment reported by the European Commission",
    "currency": "EUR",
    "temporal_granularity": "year"
  },
  "mapping": {
    "amount": {
      "type": "value",
      "label": "Amount",
      "description": "",
      "column": "amount",
      "datatype": "float"
    },
    "total": {
      "type": "value",
      "label": "Total",
      "description": "",
      "column": "total",
      "datatype": "float"
    },
    "time": {
      "type": "value",
      "label": "Year",
      "description": "",
      "column": "date",
      "datatype": "date"
    },
    "from": {
      "label": "Responsible Department",
      "type": "entity",
      "facet": true,
      "description": "EC Directorate-General",
      "fields": [
        {"column": "responsible_department", "name": "label", "datatype": "string"},
        {"constant": "true", "name": "fts_department", "datatype": "constant"}
      ]
    },
    "to": {
      "label": "Beneficiary",
      "type": "entity",
      "facet": true,
      "description": "",
      "fields": [
        {"column": "beneficiary", "name": "label", "datatype": "string"},
        {"column": "alias", "name": "alias", "datatype": "string"},
        {"column": "address", "name": "address", "datatype": "string"},
        {"column": "city", "name": "city", "datatype": "string"},
        {"column": "post_code", "name": "post_code", "datatype": "string"},
        {"column": "country", "name": "country", "datatype": "string"},
        {"column": "geozone", "name": "geozone", "datatype": "string"},
        {"column": "coordinator", "name": "coordinator", "datatype": "string"},
        {"constant": "yes", "name": "fts_beneficiary", "datatype": "constant"}
      ]
    },
    "action_type": {
      "label": "Action Type",
      "type": "classifier",
      "taxonomy": "ec-action-type",
      "description": "",
      "facet": true,
      "fields": [
        {"column": "action_type", "name": "label", "datatype": "string"}
      ]
    },
    "title": {
      "label": "Budget Title",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "",
      "facet": true,
      "fields": [
        {"column": "title", "name": "name", "datatype": "string"}
      ]
    },
    "chapter": {
      "label": "Budget Chapter",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "",
      "fields": [
        {"column": "chapter", "name": "name", "datatype": "string"}
      ]
    },
    "article": {
      "label": "Budget Article",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "",
      "fields": [
        {"column": "article", "name": "name", "datatype": "string"}
      ]
    },
    "item": {
      "label": "Budget Item",
      "type": "classifier",
      "taxonomy": "eu",
      "description": "",
      "fields": [
        {"column": "item", "name": "name", "datatype": "string"}
      ]
    },
    "grant_subject": {
      "type": "value",
      "label": "Grant Subject",
      "description": "Short description",
      "column": "grant_subject",
      "datatype": "string"
    },
    "budget_item": {
      "type": "value",
      "label": "Budget Item",
      "description": "",
      "column": "budget_item",
      "datatype": "string"
    },
    "cofinancing_rate": {
      "type": "value",
      "label": "Co-financing rate",
      "description": "The co-financing rate of a project total financing corresponds to the portion (expressed in %) financed by the EU. Alongside EU financing, many projects may/must receive national, private or international financing.",
      "column": "cofinancing_rate",
      "datatype": "string"
    },
    "position_key": {
      "type": "value",
      "label": "Position Key",
      "description": "",
      "column": "grant_subject",
      "datatype": "string"
    },
    "country": {
      "type": "value",
      "label": "Country",
      "description": "",
      "column": "country",
      "datatype": "string"
    }
  },
  "views": [
    {
      "entity": "dataset",
      "label": "Directorate-General",
      "name": "default",
      "dimension": "dataset",
      "breakdown": "from",
      "filters": {"name": "ecfts"}
    },
    {
      "entity": "dataset",
      "label": "Action Type",
      "name": "action_type",
      "dimension": "dataset",
      "breakdown": "action_type",
      "filters": {"name": "ecfts"}
    },
    {
      "entity": "entity",
      "label": "Budget Article",
      "name": "default",
      "dimension": "from",
      "breakdown": "article",
      "filters": {"fts_department": "yes"}
    },
    {
      "entity": "entity",
      "label": "Action Type",
      "name": "action_type",
      "dimension": "from",
      "breakdown": "action_type",
      "filters": {"fts_department": "yes"}
    },
    {
      "entity": "classifier",
      "label": "Action Type",
      "name": "default",
      "dimension": "article",
      "breakdown": "action_type",
      "filters": {"taxonomy": "eu", "level_name": "article"}
    },
    {
      "entity": "classifier",
      "label": "Action Type",
      "name": "default",
      "dimension": "item",
      "breakdown": "action_type",
      "filters": {"taxonomy": "eu", "level_name": "item"}
    },
    {
      "entity": "classifier",
      "label": "Recipient Countries",
      "name": "member",
      "dimension": "article",
      "breakdown": "country",
      "filters": {"taxonomy": "eu", "level_name": "article"}
    },
    {
      "entity": "classifier",
      "label": "Recipient Countries",
      "name": "member",
      "dimension": "item",
      "breakdown": "country",
      "filters": {"taxonomy": "eu", "level_name": "item"}
    },
    {
      "entity": "classifier",
      "label": "Recipients",
      "name": "bene",
      "dimension": "article",
      "breakdown": "to",
      "filters": {"taxonomy": "eu", "level_name": "article"}
    },
    {
      "entity": "classifier",
      "label": "Recipients",
      "name": "bene",
      "dimension": "item",
      "breakdown": "to",
      "filters": {"taxonomy": "eu", "level_name": "item"}
    }
  ]
}

