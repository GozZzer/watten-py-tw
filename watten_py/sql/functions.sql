CREATE OR REPLACE FUNCTION uuid_macaddr(id uuid)
  RETURNS macaddr AS
$BODY$
  select substring(id::text, 25, 12)::macaddr
$BODY$
  LANGUAGE sql IMMUTABLE STRICT
  COST 100;

CREATE OR REPLACE FUNCTION uuid_timestamp(id uuid)
  RETURNS timestamp with time zone AS
$BODY$
  select TIMESTAMP WITH TIME ZONE 'epoch' +
      (((('x' || lpad(split_part(id::text, '-', 1), 16, '0'))::bit(64)::bigint) +
      (('x' || lpad(split_part(id::text, '-', 2), 16, '0'))::bit(64)::bigint << 32) +
      ((('x' || lpad(split_part(id::text, '-', 3), 16, '0'))::bit(64)::bigint&4095) << 48) - 122192928000000000) / 10000000 ) * INTERVAL '1 second';
$BODY$
  LANGUAGE sql IMMUTABLE STRICT
  COST 100;