# Geospatial and multidimensional data

Geospatial test data is useful for validating map clients, spatial ETL, and database constraints without publishing real locations. Keep synthetic fixtures clearly labelled: they are not authoritative geography and should not be used for operational decisions.

## Moving point over time

[`examples/geospatial/moving_point_features.yaml`](../examples/geospatial/moving_point_features.yaml) generates five GeoJSON-shaped `Feature` objects. Longitude and latitude change at each interval, while `observed_at` advances by 60 seconds.

```yaml
output:
  count: 5
  format: json
  collection: true
type: object
properties:
  type:
    type: static
    value: Feature
  geometry:
    type: object
    properties:
      type:
        type: static
        value: Point
      coordinates:
        type: list
        min_length: 2
        max_length: 2
        sub_type:
          type: float
          num_decimals: 6
          expression: "-42.80 + interval * 0.001 if kwargs.index == 0 else -5.09 + interval * 0.0005"
  properties:
    type: object
    properties:
      id:
        type: integer
        expression: interval
      observed_at:
        type: integer
        expression: "1735689600 + interval * 60"
```

Generate the sample:

```shell
syntrend generate examples/geospatial/moving_point_features.yaml > moving_point_features.json
```

The versioned [example output](../examples/geospatial/moving_point_features.json) is deterministic because each generated value is controlled by an expression.

## Produce a GeoJSON FeatureCollection

Syntrend's JSON collection output is an array. An array of Features is useful as an intermediate fixture, but a GeoJSON document containing several Features must wrap them in a `FeatureCollection`.

```python
import json
from pathlib import Path

features = json.loads(Path("moving_point_features.json").read_text())
feature_collection = {"type": "FeatureCollection", "features": features}
Path("moving_point.geojson").write_text(json.dumps(feature_collection, indent=2))
```

For EPSG:4326 GeoJSON points, coordinate order is **longitude, latitude**. Validate both the envelope (`-180 <= longitude <= 180`, `-90 <= latitude <= 90`) and the geometry type before loading the fixture.

## Load points into PostGIS

The following example assumes the generated array was stored in `moving_point_features.json`. It preserves EPSG:4326 explicitly and uses `jsonb_array_elements` rather than string-building SQL.

```sql
CREATE TEMP TABLE moving_points (
    id integer PRIMARY KEY,
    observed_at bigint NOT NULL,
    geom geometry(Point, 4326) NOT NULL
);

WITH payload AS (
    SELECT pg_read_file('/data/moving_point_features.json')::jsonb AS document
), features AS (
    SELECT jsonb_array_elements(document) AS feature
    FROM payload
)
INSERT INTO moving_points (id, observed_at, geom)
SELECT
    (feature #>> '{properties,id}')::integer,
    (feature #>> '{properties,observed_at}')::bigint,
    ST_SetSRID(
        ST_MakePoint(
            (feature #>> '{geometry,coordinates,0}')::double precision,
            (feature #>> '{geometry,coordinates,1}')::double precision
        ),
        4326
    )
FROM features;
```

`pg_read_file` is restricted to privileged server-side paths. Application code should normally send the parsed JSON as a bound parameter or use PostgreSQL `COPY`; do not concatenate untrusted JSON into SQL.

## Lines, polygons, KML, and GML

A line is an ordered list of coordinate pairs. A polygon adds one more nesting level and every linear ring must repeat its first coordinate as its last coordinate. Synthetic polygons should also be checked with `ST_IsValid` after loading.

Syntrend already documents how nested XML objects can represent a [GML FeatureCollection](outputs.md#collections). KML can be modelled with the same XML object/list primitives, but there is no dedicated KML or GeoJSON formatter today. State this distinction in tests: a shape-compatible JSON/XML fixture is not automatically a standards-compliant exchange document.

## Reproducibility checklist

- pin the Syntrend version used to generate fixtures;
- version the YAML configuration alongside expected output;
- record CRS and axis order;
- distinguish generated data from public or authoritative data;
- validate ranges, geometry type, ring closure, and `ST_IsValid` where applicable;
- never publish production coordinates as examples without authorization.
