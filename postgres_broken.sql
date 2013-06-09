CREATE TABLE category (
	id		varchar(40),
	title		varchar(50),
	PRIMARY KEY	(id)
);

CREATE TABLE subcategory (
	parent		varchar(40)
			REFERENCES category(id),
	PRIMARY KEY	(id)
) INHERITS (category);

CREATE TYPE media_type AS ENUM ('audio', 'video');

CREATE TABLE programme (
	masterbrand	varchar(40),
	complete_title	varchar(256),
	tags		varchar[],
	pid		varchar(12),
	media_type	media_type,
	brand_pid	varchar(12),
	is_clip		boolean,
	PRIMARY KEY	(pid)
);

CREATE TABLE programme_category (
	pid		varchar(40)
			REFERENCES programme(pid),
	category_id	varchar(40)
			REFERENCES category(id),
	PRIMARY KEY	(pid, category_id)
);

CREATE TABLE availability_window (
	pid		varchar(12)
			REFERENCES programme(pid),
	start_time	timestamp,
	end_time	timestamp,
	service		varchar(40),
	PRIMARY KEY	(pid, start_time, service)
);
