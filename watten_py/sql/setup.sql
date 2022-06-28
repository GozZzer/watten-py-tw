CREATE TABLE IF NOT EXISTS public."LoginData"
(
    user_id uuid,
    user_name text,
    email text null,
    password text null,
    dummy bool default False,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS public."PlayerData"
(
    user_id uuid references public."LoginData"(user_id),
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS public."SetData"
(
    set_id bigserial,
	game_ids bigint[],
    team1_player1 uuid references public."PlayerData"(user_id),
	team1_player2 uuid references public."PlayerData"(user_id),
	team2_player1 uuid references public."PlayerData"(user_id),
	team2_player2 uuid references public."PlayerData"(user_id),
    team1_set_points integer[] DEFAULT '{}',
    team2_set_points integer[] DEFAULT '{}',
	PRIMARY KEY (set_id)
);

CREATE TABLE IF NOT EXISTS public."GameData"
(
    game_id bigserial,
    set_id bigint references public."SetData"(set_id),
    team1_points integer[] DEFAULT '{}',
    team2_points integer[] DEFAULT '{}',
	PRIMARY KEY (game_id)
);
