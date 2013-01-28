CREATE OR REPLACE FUNCTION {{sprocName}}_delete(p_in {{returnType}}) RETURNS SETOF {{returnType}} AS
$$
DECLARE
BEGIN
  RETURN DELETE FROM {{schema}}.{{tableName}}
  WHERE
{{ whereColumns }}
  RETURNING
{{ returnColumns }}
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

