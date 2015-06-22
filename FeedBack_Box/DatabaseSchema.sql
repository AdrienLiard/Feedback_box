/* INTERVIEWS DATA*/
DROP TABLE IF EXISTS [InterviewsData];
CREATE TABLE [InterviewsData] (
	guid text not null,
	question_id integer not null,
	open_value text null,
	closed_value int null
);

/* INTERVIEWS*/
DROP TABLE IF EXISTS [Interviews];
CREATE TABLE [Interviews] (
	guid text not null,
	completed int not null default 0,
	last_question int not null default -1
);

