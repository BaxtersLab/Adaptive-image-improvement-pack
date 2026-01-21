from .nodes.NexaPopupLoaderNode import NexaTagAwarePopupLoaderNode, NexaComparisonReaderNode
from .nodes.AudioTagExtractorNodeA import AudioTagExtractorNodeA
from .nodes.AudioTagExtractorNodeB import AudioTagExtractorNodeB
from .nodes.AudioImprovementArbiterNode import AudioImprovementArbiterNode
from .nodes.AudioPromptMutatorNode import AudioPromptMutatorNode
from .nodes.AudioLoggerNode import AudioLoggerNode

NODE_CLASS_MAPPINGS = {
    "NexaTagAwarePopupLoaderNode": NexaTagAwarePopupLoaderNode,
    "NexaComparisonReaderNode": NexaComparisonReaderNode,
    "AudioTagExtractorNodeA": AudioTagExtractorNodeA,
    "AudioTagExtractorNodeB": AudioTagExtractorNodeB,
    "AudioImprovementArbiterNode": AudioImprovementArbiterNode,
    "AudioPromptMutatorNode": AudioPromptMutatorNode,
    "AudioLoggerNode": AudioLoggerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NexaTagAwarePopupLoaderNode": "Nexa Tag-Aware Chat GUI",
    "NexaComparisonReaderNode": "Nexa Response Comparison Reader",
    "AudioTagExtractorNodeA": "Audio Tag Extractor A",
    "AudioTagExtractorNodeB": "Audio Tag Extractor B",
    "AudioImprovementArbiterNode": "Audio Improvement Arbiter",
    "AudioPromptMutatorNode": "Audio Prompt Mutator",
    "AudioLoggerNode": "Audio Logger",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']