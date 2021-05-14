from gym.envs.registration import register
# must inckude the version, otherwise you will get a mal-formed environment issue.
register(
    id='template-v0',
    entry_point='template_env.envs:TemplateEnv',
)
