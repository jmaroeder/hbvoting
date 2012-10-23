drop table if exists voters;
create table voters (
  voterid integer primary key autoincrement,
  assigned_id integer,
  ethnicity varchar not null,
  email varchar not null,
  mentor varchar not null,
  gender varchar not null,
  city varchar not null,
  party varchar not null
);

drop table if exists votes;
create table votes (
  voteid integer primary key,
  choice varchar not null,
  voterid integer not null,
  foreign key(voterid) references voters(voterid)
);
