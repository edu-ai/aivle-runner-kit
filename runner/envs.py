class TestEnv(object):
	def __init__(self, *args, **kwargs):
		pass

	def run(self, agent):
		raise NotImplemented

	def terminated(self, e):
		raise NotImplemented


class BaseTestEnv(TestEnv):
	def __init__(self, *args, **kwargs):
		self.agent_init = kwargs.pop('agent_init', {})
		self.env = kwargs.pop('env')
		self.evaluator = kwargs.pop('evaluator')

	def terminated(self, e):
		self.evaluator.terminated(e)
		self.evaluator.done()
		return self.evaluator.result


class SupervisedLearningTestEnv(BaseTestEnv):
	def run(self, agent, *args, **kwargs):
		self.env.reset()
		self.evaluator.reset()
		while True:
			data = self.env.pop()
			if not data:
				break
			x, y = data
			self.evaluator.step(y_true=y, y=agent.step(x), x=x)
		self.evaluator.done()
		return self.evaluator.result


class ReinforcementLearningTestEnv(BaseTestEnv):
	def __init__(self, *args, **kwargs):
		self.t_max = kwargs.pop('t_max', None)
		self.seeds = kwargs.pop('seeds', [])
		self.use_seeds = len(self.seeds) > 0
		super().__init__(*args, **kwargs)

	def run(self, agent, *args, **kwargs):
		runs = kwargs.get('runs', 1)
		if self.use_seeds:
			assert runs == len(self.seeds) and hasattr(self.env, 'random_seed')

		agent.initialize(**self.agent_init)
		self.evaluator.reset()

		for run in range(runs):
			self.evaluator.run()
			if self.use_seeds:
				self.env.random_seed = self.seeds[run]
			state = self.env.reset()
			t = 0
			while True:
				action = agent.step(state)
				next_state, reward, done, info = self.env.step(action)

				full_state = {
					'state': state, 'action': action, 'reward': reward, 'next_state': next_state, 
					'done': done, 'info': info, 't': t, 'run': run
				}
				agent.update(**full_state)
				self.evaluator.step(**full_state)

				state = next_state
				if done or self.t_max is not None and t >= self.t_max:
					break
				t += 1

		self.evaluator.done()
		return self.evaluator.result