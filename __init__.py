from .nodes.NexaPopupLoaderNode import NexaTagAwarePopupLoaderNode, NexaComparisonReaderNode
from .nodes.AudioTagExtractorNodeA import AudioTagExtractorNodeA
from .nodes.AudioTagExtractorNodeB import AudioTagExtractorNodeB
from .nodes.AudioImprovementArbiterNode import AudioImprovementArbiterNode
from .nodes.AudioPromptMutatorNode import AudioPromptMutatorNode
from .nodes.AudioLoggerNode import AudioLoggerNode

NODE_CLASS_MAPPINGS = {
    "AIP_NexaTagAwarePopupLoader": NexaTagAwarePopupLoaderNode,
    "AIP_NexaComparisonReader": NexaComparisonReaderNode,
    "AIP_AudioTagExtractorA": AudioTagExtractorNodeA,
    "AIP_AudioTagExtractorB": AudioTagExtractorNodeB,
    "AIP_AudioImprovementArbiter": AudioImprovementArbiterNode,
    "AIP_AudioPromptMutator": AudioPromptMutatorNode,
    "AIP_AudioLogger": AudioLoggerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AIP_NexaTagAwarePopupLoader": "Nexa Tag-Aware Chat GUI",
    "AIP_NexaComparisonReader": "Nexa Response Comparison Reader",
    "AIP_AudioTagExtractorA": "Audio Tag Extractor A",
    "AIP_AudioTagExtractorB": "Audio Tag Extractor B",
    "AIP_AudioImprovementArbiter": "Audio Improvement Arbiter",
    "AIP_AudioPromptMutator": "Audio Prompt Mutator",
    "AIP_AudioLogger": "Audio Logger",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']