from gym.envs.registration import register

register(
    id='walk-forward-v0',
    entry_point='gym_soccerbot.envs:WalkingForward',
)
