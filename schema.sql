DROP TABLE IF EXISTS pings;
CREATE TABLE pings (
	device_id varchar[40] NOT NULL,
	epoch_time timestamp[10] NOT NULL
);