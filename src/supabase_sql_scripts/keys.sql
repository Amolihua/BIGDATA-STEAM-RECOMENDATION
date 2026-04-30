
ALTER TABLE public.users ADD PRIMARY KEY (user_id);
ALTER TABLE public.games ADD PRIMARY KEY (app_id);
ALTER TABLE public.games_metadata ADD PRIMARY KEY (app_id);
ALTER TABLE public.recommendations ADD PRIMARY KEY (review_id);


ALTER TABLE public.games_metadata 
  ADD CONSTRAINT fk_metadata_game 
  FOREIGN KEY (app_id) REFERENCES public.games(app_id)
  ON DELETE CASCADE;


ALTER TABLE public.recommendations 
  ADD CONSTRAINT fk_recommendation_user 
  FOREIGN KEY (user_id) REFERENCES public.users(user_id)
  ON DELETE CASCADE;


ALTER TABLE public.recommendations 
  ADD CONSTRAINT fk_recommendation_game 
  FOREIGN KEY (app_id) REFERENCES public.games(app_id)
  ON DELETE CASCADE;
