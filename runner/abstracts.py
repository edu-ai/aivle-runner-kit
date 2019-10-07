# Test Creator

from gym import Env as GymEnv

class Env(GymEnv):
    pass

class Generator(object):
    def __init__(self, *args, **kwargs):
        pass

    def reset(self):
        raise NotImplementedError

    def pop(self):
        raise NotImplementedError

class EvaluationResult(object):
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self):
        raise NotImplementedError

    def __int__(self):
        raise NotImplementedError

    @property
    def json(self):
        raise NotImplementedError

class Evaluator(object):
    def __init__(self, *args, **kwargs):
        pass

    def reset(self, *args, **kwargs):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        pass

    def step(self, *args, **kwargs):
        raise NotImplementedError

    def done(self, *args, **kwargs):
        raise NotImplementedError

    def terminated(self, e):
        return

    @property
    def result(self):
        return EvaluationResult()

def compute_point(results):
    raise NotImplementedError


# Test Taker

class Agent(object):
    def __init__(self, *args, **kwargs):
        pass

    def initialize(self, **kwargs):
        pass

    def step(self, state, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        return

def create_agent(test_case_id, *args, **kwargs):
    raise NotImplementedError