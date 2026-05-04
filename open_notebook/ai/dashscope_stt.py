"""DashScope (Qwen) Speech-to-Text provider wrapper.

This module provides a wrapper for DashScope's Paraformer STT API
that conforms to esperanto's SpeechToTextModel interface.

Uses the Recognition API which supports local file transcription.
"""

import os
import tempfile
from typing import Any, BinaryIO, Dict, List, Optional, Union

from esperanto.common_types import Model, TranscriptionResponse
from esperanto.providers.stt.base import SpeechToTextModel
from loguru import logger


class DashScopeSpeechToTextModel(SpeechToTextModel):
    """DashScope Paraformer Speech-to-Text provider.

    Supports Paraformer realtime models for high-quality Chinese and multi-language STT.

    Example:
        >>> stt = DashScopeSpeechToTextModel(
        ...     model_name="paraformer-realtime-v2",
        ...     api_key="your-dashscope-api-key"
        ... )
        >>> response = stt.transcribe("audio.mp3")
    """

    # Valid model names for DashScope Recognition API
    # (tested against actual API - other names return ModelNotFound)
    VALID_MODELS = [
        "paraformer-realtime-v1",
        "paraformer-realtime-v2",
        "paraformer-realtime-8k-v1",
    ]

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize DashScope STT provider.

        Args:
            model_name: Name of the STT model (e.g., 'paraformer-realtime-v2')
            api_key: DashScope API key
            base_url: Optional base URL (not used, DashScope SDK handles this)
            config: Additional configuration
            **kwargs: Additional parameters
        """
        # Merge config and kwargs
        config = config or {}
        config.update(kwargs)

        # Set API key from parameter or environment
        self.api_key = api_key or config.get("api_key") or os.getenv("DASHSCOPE_API_KEY")

        # Call parent's __post_init__ after setting attributes
        super().__post_init__()

        # Set model name - map old names to valid ones
        self.model_name = model_name or self._get_default_model()
        # Auto-correct model name if using invalid format
        if self.model_name not in self.VALID_MODELS:
            # Map common invalid names to valid ones
            name_mapping = {
                "paraformer-v1": "paraformer-realtime-v1",
                "paraformer-v2": "paraformer-realtime-v2",
                "paraformer-8k-v1": "paraformer-realtime-8k-v1",
                "paraformer-realtime": "paraformer-realtime-v1",
                "sensevoice-v1": "paraformer-realtime-v2",  # fallback
            }
            corrected = name_mapping.get(self.model_name)
            if corrected:
                logger.debug(f"Mapping model name {self.model_name} -> {corrected}")
                self.model_name = corrected
            else:
                logger.warning(f"Unknown model name {self.model_name}, using default")
                self.model_name = self._get_default_model()

        # Initialize DashScope SDK
        if self.api_key:
            import dashscope
            dashscope.api_key = self.api_key

        logger.debug(f"Initialized DashScope STT with model={self.model_name}")

    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "dashscope"

    def _get_default_model(self) -> str:
        """Get the default model name."""
        return "paraformer-realtime-v2"

    def _get_models(self) -> List[Model]:
        """Get available models for DashScope STT."""
        return [
            Model(id="paraformer-realtime-v1", owned_by="alibaba", context_window=None),
            Model(id="paraformer-realtime-v2", owned_by="alibaba", context_window=None),
            Model(id="paraformer-realtime-8k-v1", owned_by="alibaba", context_window=None),
        ]

    def transcribe(
        self,
        audio_file: Union[str, BinaryIO],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> TranscriptionResponse:
        """Transcribe audio to text using DashScope Recognition API.

        Args:
            audio_file: Path to audio file or file-like object
            language: Optional language code (e.g., 'zh', 'en')
            prompt: Optional text to guide transcription (not supported by DashScope)

        Returns:
            TranscriptionResponse containing the transcribed text
        """
        try:
            from dashscope.audio.asr import Recognition, RecognitionCallback

            # Simple callback for synchronous transcription
            class SyncCallback(RecognitionCallback):
                def __init__(self):
                    self.result = None
                    self.error = None

                def on_open(self):
                    pass

                def on_complete(self):
                    pass

                def on_error(self, error):
                    self.error = str(error)

                def on_close(self):
                    pass

            # Handle file input
            if isinstance(audio_file, str):
                # Determine format from file extension
                import mimetypes
                mime_type, _ = mimetypes.guess_type(audio_file)
                if not mime_type:
                    mime_type = "audio/wav"

                # Map mime type to format string for DashScope
                format_mapping = {
                    "audio/wav": "wav",
                    "audio/mpeg": "mp3",
                    "audio/mp3": "mp3",
                    "audio/ogg": "ogg",
                    "audio/flac": "flac",
                    "audio/m4a": "m4a",
                    "audio/mp4": "mp4",
                }
                format = format_mapping.get(mime_type, "wav")

                # Create recognition with callback
                callback = SyncCallback()
                recognition = Recognition(
                    model=self.model_name,
                    callback=callback,
                    format=format,
                    sample_rate=16000,  # Default sample rate
                )

                result = recognition.call(file=audio_file)

                # Check status code first
                if result.status_code != 200:
                    error_msg = result.message or f"HTTP {result.status_code}"
                    raise RuntimeError(f"DashScope STT failed: {error_msg}")

                # Extract text from result
                sentences = result.get_sentence()
                if sentences:
                    text = ""
                    for sentence in sentences:
                        text += sentence.get("text", "")
                    detected_language = language or "zh"
                else:
                    # No speech detected - return empty transcription
                    text = ""
                    detected_language = language or "unknown"

            else:
                # For BinaryIO, save to temp file first
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name

                try:
                    return self.transcribe(tmp_path, language=language, prompt=prompt)
                finally:
                    os.unlink(tmp_path)

            return TranscriptionResponse(
                text=text,
                language=detected_language,
                model=self.model_name,
            )

        except ImportError:
            raise RuntimeError("DashScope SDK not installed. Install with: pip install dashscope")
        except Exception as e:
            raise RuntimeError(f"Failed to transcribe audio with DashScope: {str(e)}") from e

    async def atranscribe(
        self,
        audio_file: Union[str, BinaryIO],
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> TranscriptionResponse:
        """Async transcribe audio to text.

        Note: DashScope SDK doesn't have native async support for STT,
        so we run the sync version in a thread pool.
        """
        import asyncio
        from functools import partial

        # For BinaryIO, we need to read the content first since
        # running in executor will lose access to the file object
        if not isinstance(audio_file, str):
            content = audio_file.read()
            func = partial(
                self._transcribe_from_bytes,
                audio_data=content,
                language=language,
                prompt=prompt,
            )
        else:
            func = partial(
                self.transcribe,
                audio_file=audio_file,
                language=language,
                prompt=prompt,
            )

        return await asyncio.get_event_loop().run_in_executor(None, func)

    def _transcribe_from_bytes(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> TranscriptionResponse:
        """Helper to transcribe from raw bytes."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            return self.transcribe(tmp_path, language=language, prompt=prompt)
        finally:
            os.unlink(tmp_path)