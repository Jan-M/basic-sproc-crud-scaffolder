CREATE OR REPLACE FUNCTION {{sprocName}}_create(p_in {{returnType}}) RETURNS SETOF {{returnType}} AS
$$
DECLARE
BEGIN
  RETURN QUERY INSERT INTO {{schema}}.{{tableName}} (
{{columns}}
  )
  SELECT
{{ insertValues }}
  RETURNING
{{ returnColumns }};
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

