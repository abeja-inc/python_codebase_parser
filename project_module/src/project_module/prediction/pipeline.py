from abc import ABC, abstractmethod

from .io import PredictionPipelineInput, PredictionPipelineOutput


class BasePredictionPipeline(ABC):
    @abstractmethod
    def run(self, inputs: PredictionPipelineInput) -> PredictionPipelineOutput:
        raise NotImplementedError


class PredictionPipeline(BasePredictionPipeline):
    # TODO: Implement the prediction pipeline
    pass
