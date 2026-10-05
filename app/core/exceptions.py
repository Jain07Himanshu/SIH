class GrievanceEngineError(Exception):
    pass

class ValidationError(GrievanceEngineError):
    pass

class DatasetAdapterError(GrievanceEngineError):
    pass

class ModelLoadError(GrievanceEngineError):
    pass

class EmbeddingError(GrievanceEngineError):
    pass

class ClusteringError(GrievanceEngineError):
    pass

class IssueNotFoundError(GrievanceEngineError):
    pass
