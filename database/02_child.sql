CREATE TABLE child (
  c_id serial primary key,
  c_name text,
  c_first_name text,
  c_parent_id int references parent ( p_id ),
  c_enabled boolean
);
