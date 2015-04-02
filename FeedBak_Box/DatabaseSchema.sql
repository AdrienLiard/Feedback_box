/* QUESTIONS */
DROP TABLE IF EXISTS [Questions];
CREATE TABLE [Questions] (
	id integer primary key autoincrement,
	question_order integer not null,
	name text not null,
	[text] text not null,
	type integer not null,
	max_responses integer not null,
	authorize_nr integer not null default 0
);

/* QUESTION TYPES */
DROP TABLE IF EXISTS [QuestionTypes];
CREATE TABLE [QuestionTypes] (
	id integer primary key autoincrement,
	name text not null
);
INSERT INTO [QuestionTypes] (name) values ('Open');
INSERT INTO [QuestionTypes] (name) values ('Numeric');
INSERT INTO [QuestionTypes] (name) values ('Single');
INSERT INTO [QuestionTypes] (name) values ('Multiple');

/* RESPONSES */
DROP TABLE IF EXISTS [Responses];
CREATE TABLE [Responses] (
	id integer primary key autoincrement,
	guid text not null,
	questionId integer not null,
	response_order integer not null,
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

