{
  "dataset": {
    "name": "eu-commission-fts",
    "label": "EU Commission Grants & Commitments", 
    "description": "All grants and commitment reported by the European Commission",
    "currency": "EUR"
  },
  "mapping": {
    "amount": {
      "type": "measure",
      "label": "Amount",
      "description": "",
      "column": "amount",
      "datatype": "float"
    },
    "total": {
      "type": "measure",
      "label": "Total",
      "description": "",
      "column": "total",
      "datatype": "float"
    },
    "time": {
      "type": "date",
      "label": "Year",
      "description": "",
      "column": "date",
      "key": true,
      "datatype": "date"
    },
    "from": {
      "label": "Responsible Department",
      "type": "entity",
      "facet": true,
      "key": true,
      "description": "EC Directorate-General",
      "fields": [
        {"column": "department_name", "name": "name", "datatype": "id"},
        {"column": "department_name", "name": "label", "datatype": "string"},
        {"column": "department_uri", "name": "uri", "datatype": "string"},
        {"column": "responsible_department", "name": "original_name", "datatype": "string"}
      ]
    },
    "to": {
      "label": "Beneficiary",
      "type": "compound",
      "facet": true,
      "key": true,
      "description": "",
      "fields": [
        {"column": "beneficiary", "name": "name", "datatype": "id"},
        {"column": "beneficiary", "name": "label", "datatype": "string"},
        {"column": "alias", "name": "alias", "datatype": "string"},
        {"column": "address", "name": "address", "datatype": "string"},
        {"column": "city", "name": "city", "datatype": "string"},
        {"column": "postcode", "name": "postcode", "datatype": "string"},
        {"column": "country", "name": "country", "datatype": "string"},
        {"column": "geozone", "name": "geozone", "datatype": "string"}
      ]
    },
    "action_type": {
      "label": "Action Type",
      "type": "compound",
      "description": "",
      "facet": true,
      "fields": [
        {"column": "action_type", "name": "name", "datatype": "id",
          "default_value": "unknown-action"},
        {"column": "action_type", "name": "label", "datatype": "string",
          "default_value": "(Unknown Action)"}
      ]
    },
    "title": {
      "label": "Budget Title",
      "type": "compound",
      "description": "",
      "facet": true,
      "fields": [
        {"column": "title_name", "name": "name", "datatype": "id",
          "default_value": "unknown"},
        {"column": "title_label", "name": "label", "datatype": "string",
          "default_value": "(Unknown Title)"},
        {"column": "title_description", "name": "description", "datatype": "string"},
        {"column": "title_legal_basis", "name": "legal_basis", "datatype": "string"}
      ]
    },
    "chapter": {
      "label": "Budget Chapter",
      "type": "compound",
      "description": "",
      "fields": [
        {"column": "chapter_name", "name": "name", "datatype": "id",
          "default_value": "unknown"},
        {"column": "chapter_label", "name": "label", "datatype": "string",
          "default_value": "(Unknown Chapter)"},
        {"column": "chapter_description", "name": "description", "datatype": "string"},
        {"column": "chapter_legal_basis", "name": "legal_basis", "datatype": "string"}
      ]
    },
    "article": {
      "label": "Budget Article",
      "type": "compound",
      "description": "",
      "fields": [
        {"column": "article_name", "name": "name", "datatype": "id",
          "default_value": "unknown"},
        {"column": "article_label", "name": "label", "datatype": "string",
          "default_value": "(Unknown Article)"},
        {"column": "article_description", "name": "description", "datatype": "string"},
        {"column": "article_legal_basis", "name": "legal_basis", "datatype": "string"}
      ]
    },
    "item": {
      "label": "Budget Item",
      "type": "compound",
      "description": "",
      "fields": [
        {"column": "item_name", "name": "name", "datatype": "id",
          "default_value": "unknown"},
        {"column": "item_label", "name": "label", "datatype": "string",
          "default_value": "(Unknown Item)"},
        {"column": "item_description", "name": "description", "datatype": "string"},
        {"column": "item_legal_basis", "name": "legal_basis", "datatype": "string"}
      ]
    },
    "coordinator": {
      "type": "attribute",
      "label": "Coordinator",
      "description": "Beneficiary leads this project",
      "column": "coordinator",
      "key": true,
      "datatype": "string"
    },
    "source_id": {
      "type": "attribute",
      "label": "Source ID (OS internal use)",
      "description": "",
      "column": "source_id",
      "key": true,
      "datatype": "string"
    },
    "grant_subject": {
      "type": "attribute",
      "label": "Grant Subject",
      "description": "Short description",
      "column": "grant_subject",
      "key": true,
      "datatype": "string"
    },
    "cofinancing_rate": {
      "type": "attribute",
      "label": "Co-financing rate",
      "description": "The co-financing rate of a project total financing corresponds to the portion (expressed in %) financed by the EU. Alongside EU financing, many projects may/must receive national, private or international financing.",
      "column": "cofinancing_rate",
      "datatype": "string"
    },
    "position_key": {
      "type": "attribute",
      "label": "Position Key",
      "description": "",
      "key": true,
      "column": "grant_subject",
      "datatype": "string"
    },
    "country": {
      "type": "compound",
      "label": "Country",
      "description": "",
      "fields": [
        {"column": "country_code", "name": "name", "datatype": "id",
          "default_value": "XX"},
        {"column": "country_name", "name": "label", "datatype": "string",
          "default_value": "(Unknown Country)"}
      ]
    }
  },
  "views": [
    {
      "entity": "dataset",
      "label": "Directorate-General",
      "name": "default",
      "dimension": "dataset",
      "drilldown": "from"
    },
    {
      "entity": "dataset",
      "label": "Action Type",
      "name": "action_type",
      "dimension": "dataset",
      "drilldown": "action_type"
    },
    {
      "entity": "dimension",
      "label": "Budget Article",
      "name": "default",
      "dimension": "from",
      "drilldown": "article"
    },
    {
      "entity": "dimension",
      "label": "Action Type",
      "name": "action_type",
      "dimension": "from",
      "drilldown": "action_type"
    },
    {
      "entity": "dimension",
      "label": "Action Type",
      "name": "default",
      "dimension": "article",
      "drilldown": "action_type"
    },
    {
      "entity": "dimension",
      "label": "Action Type",
      "name": "default",
      "dimension": "item",
      "drilldown": "action_type"
    },
    {
      "entity": "dimension",
      "label": "Recipient Countries",
      "name": "member",
      "dimension": "article",
      "drilldown": "country"
    },
    {
      "entity": "dimension",
      "label": "Recipient Countries",
      "name": "member",
      "dimension": "item",
      "drilldown": "country"
    },
    {
      "entity": "dimension",
      "label": "Recipients",
      "name": "beneficiary",
      "dimension": "article",
      "drilldown": "to"
    },
    {
      "entity": "dimension",
      "label": "Recipients",
      "name": "beneficiary",
      "dimension": "item",
      "drilldown": "to"
    }
  ]
}

