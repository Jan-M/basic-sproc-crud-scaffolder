CREATE OR REPLACE FUNCTION {{sprocName}}_update(p_in {{returnType}}) RETURNS SETOF {{returnType}} AS
$$
DECLARE 
BEGIN
  RETURN QUERY UPDATE {{schema}}.{{tableName}} 
  SET
{{ updateColumns }}
  WHERE
{{ whereColumns }}
  RETURNING
{{ returnColumns }}
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

