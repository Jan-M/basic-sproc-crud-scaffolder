CREATE OR REPLACE FUNCTION {{ sprocName }}_get_by_{{ uniqueKeyName }}({{ keyColumns }}) RETURNS SETOF {{ returnType }} AS
$$
DECLARE 
BEGIN
  RETURN QUERY SELECT
{{ selectColumns }}
  FROM {{schema}}.{{tableName}}
  WHERE
{{ whereColumns }}
  ;
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

