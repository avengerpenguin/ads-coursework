
BEGIN TRANSACTION;

DROP TABLE IF EXISTS availability_window;
DROP TABLE IF EXISTS subcategory;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS programme;
DROP TYPE IF EXISTS media_type;

CREATE TABLE category (
  id    varchar,
  title varchar
);

CREATE TABLE subcategory (
  parent category
) INHERITS (category);

CREATE TYPE media_type AS ENUM ('audio', 'video') ;
CREATE TABLE programme (
	masterbrand	varchar(20),
	complete_title	varchar(256),
	tags	varchar[],
	pid	varchar(10),
	media_type	media_type,
	brand_pid	varchar(10),
	is_clip	boolean
);

INSERT INTO programme (masterbrand,complete_title,tags,pid,media_type,brand_pid,is_clip) VALUES ('bbc_radio_four','in_our_time:_democracy','{"democracy", "history", "philosophy", "plato", "ancient_greece"}','p00547jm','audio','b006qykl','0');
COMMIT;
