python -m baselines.run --alg=ppo2 --env=gym_soccerbot:walk-forward-v0 --network=mlp --num_timesteps=2 --ent_coef=0.1 --num_hidden=32 --num_layers=3 --save_path=./model1

python -m baselines.run --alg=ppo2 --env=gym_soccerbot:walk-forward-v0 --network=mlp --num_timesteps=0 --ent_coef=0.1 --num_hidden=32 --num_layers=3 --load_path=./model1 --play
