from .abstracts import EvaluationResult, Evaluator

DEFAULT_ERROR_VALUE = 0.0

class BaseEvaluationResult(EvaluationResult):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'score')
        self.value = kwargs.get('value')
        self.results = kwargs.get('results', [])
        self.error = kwargs.get('error', None)

    def __str__(self):
        if self.error: 
            return "{}: {}".format(type(self.error).__name__, str(self.error))
        str_results = " ".join(map(lambda x: str(x), self.results))
        return str_results

    def __int__(self):
        return int(float(self))

    def __float__(self):
        if self.error: return DEFAULT_ERROR_VALUE
        return float(round(self.value, 3))

    @property
    def json(self):
        return {
            self.name: self.__float__(),
            'details': self.__str__()
        }

class BaseEvaluator(Evaluator):
    def __init__(self, *args, **kwargs):
        self.error = None
        self.average = kwargs.get('average', False)

    def reset(self, *args, **kwargs):
        self.error = None

    def run(self, *args, **kwargs):
        pass

    def terminated(self, e):
        self.error = e

class SklearnMetricEvaluator(BaseEvaluator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metric = kwargs.get('metric')
        self.metric_kwargs = kwargs.get('metric_kwargs', {})
        self.result_class = kwargs.get('result_class', None)
        self.reset()
        
    def reset(self, *args, **kwargs):
        super().reset(*args, **kwargs)
        self.ys_true = []
        self.ys = []

    def step(self, *args, **kwargs):
        self.ys_true.append(kwargs.get('y_true'))
        self.ys.append(kwargs.get('y'))

    def done(self, *args, **kwargs):
        self.value = self.metric(self.ys_true, self.ys, **self.metric_kwargs)

    @property
    def result(self):
        results=(self.ys_true, self.ys)
        if self.result_class:
            return self.result_class(name=self.metric.__name__, value=self.value, results=results, error=self.error)
        return BaseEvaluationResult(name=self.metric.__name__, value=self.value, results=results, error=self.error)

class RewardEvaluator(BaseEvaluator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset()
        
    def reset(self, *args, **kwargs):
        self.runs = []

    def run(self, *args, **kwargs):
        self.runs.append([])

    def step(self, *args, **kwargs):
        if len(self.runs) == 0: # Backward compatibility
            self.run()
        self.runs[-1].append(kwargs.get('reward'))

    def done(self, *args, **kwargs):
        self.run_length = len(self.runs)
        self.run_cum_rewards = [sum(rewards) for rewards in self.runs]
        self.cum_rewards = sum(self.run_cum_rewards)
        if self.average:
            self.cum_rewards = self.cum_rewards / self.run_length

    @property
    def result(self):
        name = 'cumulative rewards'
        if self.run_length > 1:
            name = "{} runs {}".format(self.run_length, name)
            name = "{} {}".format('averaged' if self.average else 'sum', name)
        rewards = self.runs[0] if self.run_length == 1 else self.run_cum_rewards
        return BaseEvaluationResult(name=name, value=self.cum_rewards, results=rewards, error=self.error)

class ComputePoint:
    def sum_values(results):
        return sum([float(res.evaluation) for res in results])

    def sum_positives(results):
        return sum([float(res.evaluation) for res in results if float(res.evaluation) > 0])

    def count_positives(results):
        return sum([1 for res in results if float(res.evaluation) > 0])

    def average_values(results):
        return ComputePoint.sum_values(results)/len(results)