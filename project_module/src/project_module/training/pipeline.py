from abc import ABC, abstractmethod

from .io import TrainingPipelineInput, TrainingPipelineOutput


class BaseTrainingPipeline(ABC):
    @abstractmethod
    def run(self, inputs: TrainingPipelineInput) -> TrainingPipelineOutput:
        pass


class TrainingPipeline(BaseTrainingPipeline):
    # TODO: Implement the training pipeline
    pass
