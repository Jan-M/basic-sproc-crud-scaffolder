CREATE OR REPLACE FUNCTION insert{{sprocName}}(p_in {{returnType}}) RETURNS SETOF {{returnType}} AS
$$
DECLARE 
  RETURN QUERY INSERT INTO {{schema}}.{{tableName}} (
    {{columns}}
  )
  SELECT
    {{ insertValues }}
  RETURNING
    {{ returnColumns }}
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

