CREATE TABLE parent (
  p_id serial primary key,
  p_name text,
  p_last_name text,
  p_parent_data_id integer references parent_data ( pd_id )
 );
