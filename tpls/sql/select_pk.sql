CREATE OR REPLACE FUNCTION select{{sprocName}}(p_in {{returnType}}) RETURNS SETOF {{returnType}} AS
$$
DECLARE 
BEGIN
  RETURN QUERY SELECT
    {{ selectColumns }}
  WHERE
    {{ whereColumns }}
  ;
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;

