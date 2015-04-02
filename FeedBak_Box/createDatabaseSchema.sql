/* QUESTIONS */
DROP TABLE IF EXISTS [Questions];
CREATE TABLE [Questions] (
	id integer primary key autoincrement,
	title text not null,
	type integer not null,
	max_responses integer not null,
	authorize_nr integer not null default 0
);

/* RESPONSES */
DROP TABLE IF EXISTS [Responses];
CREATE TABLE [Responses] (
	id integer primary key autoincrement,
	guid text not null,
	questionId integer not null,
	order integer not null,
	title text not null,
	is_exclusive integer not null default 0
);


/* INTERVIEWS */
DROP TABLE IF EXISTS [Interviews];
CREATE TABLE [Interviews] (
	id integer not null,
	question_id integer not null,
	open_value text null,
	closed_value int null
);

