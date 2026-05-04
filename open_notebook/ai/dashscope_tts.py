"""DashScope (Qwen) Text-to-Speech provider wrapper.

This module provides a wrapper for DashScope's TTS API (qwen3-tts-instruct-flash)
that conforms to esperanto's TextToSpeechModel interface.

Uses the multimodal-generation API endpoint for TTS.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx

from esperanto.common_types import Model
from esperanto.common_types.tts import AudioResponse, Voice
from esperanto.providers.tts.base import TextToSpeechModel
from loguru import logger


# DashScope multimodal TTS API endpoint
DASHSCOPE_TTS_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"


class DashScopeTextToSpeechModel(TextToSpeechModel):
    """DashScope TTS provider using multimodal-generation API.

    Supports qwen3-tts-instruct-flash model for high-quality TTS.

    Example:
        >>> tts = DashScopeTextToSpeechModel(
        ...     model_name="qwen3-tts-instruct-flash",
        ...     api_key="your-dashscope-api-key"
        ... )
        >>> response = tts.generate_speech("你好，世界")
    """

    # Supported TTS models
    SUPPORTED_MODELS = [
        "qwen3-tts-instruct-flash",
        "qwen3-tts-vd-2026-01-26",
        "qwen3-tts-vc-2026-01-22",
    ]

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize DashScope TTS provider.

        Args:
            model_name: Name of the TTS model (e.g., 'qwen3-tts-instruct-flash')
            api_key: DashScope API key
            base_url: Optional base URL (defaults to multimodal-generation endpoint)
            config: Additional configuration
            **kwargs: Additional parameters
        """
        # Merge config and kwargs
        config = config or {}
        config.update(kwargs)

        # Set API key from parameter or environment
        self.api_key = api_key or config.get("api_key") or os.getenv("DASHSCOPE_API_KEY")

        # Use provided base_url or default to multimodal-generation endpoint
        self.base_url = base_url or config.get("base_url") or DASHSCOPE_TTS_API_URL

        # Call parent's __post_init__ after setting attributes
        super().__post_init__()

        # Set model name (default to qwen3-tts-instruct-flash)
        self.model_name = model_name or self._get_default_model()

        # Create HTTP client (disable proxy for direct API access)
        self._http_client = httpx.Client(
            trust_env=False,
            timeout=60.0
        )

        logger.debug(f"Initialized DashScope TTS with model={self.model_name}")

    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "dashscope"

    def _get_default_model(self) -> str:
        """Get the default model name."""
        return "qwen3-tts-instruct-flash"

    def _get_models(self) -> List[Model]:
        """Get available models for DashScope TTS."""
        return [
            Model(id="qwen3-tts-instruct-flash", owned_by="alibaba", context_window=None),
            Model(id="qwen3-tts-vd-2026-01-26", owned_by="alibaba", context_window=None),
            Model(id="qwen3-tts-vc-2026-01-22", owned_by="alibaba", context_window=None),
        ]

    @property
    def available_voices(self) -> Dict[str, Voice]:
        """Get available voices for DashScope TTS.

        Note: qwen3-tts models may not support explicit voice selection.
        Returns default voices for compatibility.
        """
        return {
            "default": Voice(
                id="default",
                name="Default",
                gender="NEUTRAL",
                language_code="zh-CN",
                description="Default voice for DashScope TTS"
            ),
        }

    def generate_speech(
        self,
        text: str,
        voice: str = None,
        output_file: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> AudioResponse:
        """Generate speech from text using DashScope multimodal TTS API.

        Args:
            text: Text to convert to speech
            voice: Voice ID (not used by qwen3-tts, kept for interface compatibility)
            output_file: Optional path to save the audio file
            **kwargs: Additional parameters

        Returns:
            AudioResponse containing the audio data
        """
        self.validate_parameters(text, voice or "default")

        if not self.api_key:
            raise RuntimeError("DashScope API key not configured")

        try:
            # Build request payload for multimodal-generation API
            payload = {
                "model": self.model_name,
                "input": {
                    "text": text
                }
            }

            # Make API request
            response = self._http_client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                except Exception:
                    error_data = {}
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
                raise RuntimeError(f"DashScope TTS API error: {error_msg}")

            data = response.json()

            # Get audio URL from response
            audio_info = data.get("output", {}).get("audio", {})
            audio_url = audio_info.get("url")

            if not audio_url:
                raise RuntimeError("No audio URL in DashScope response")

            # Download audio from URL
            audio_response = self._http_client.get(audio_url)
            if audio_response.status_code != 200:
                raise RuntimeError(f"Failed to download audio: HTTP {audio_response.status_code}")

            audio_data = audio_response.content

            # Determine format from URL or response
            audio_format = "wav" if ".wav" in audio_url.lower() else "mp3"

            # Save to file if specified
            if output_file:
                self.save_audio(audio_data, output_file)

            return AudioResponse(
                audio_data=audio_data,
                content_type=f"audio/{audio_format}",
                model=self.model_name,
                voice=voice or "default",
                provider=self.provider,
                metadata={"text": text, "format": audio_format}
            )

        except Exception as e:
            raise RuntimeError(f"Failed to generate speech with DashScope: {str(e)}") from e

    async def agenerate_speech(
        self,
        text: str,
        voice: str = None,
        output_file: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> AudioResponse:
        """Async generate speech from text.

        Note: Uses sync version in executor since httpx async client
        requires separate setup.
        """
        import asyncio
        from functools import partial

        func = partial(
            self.generate_speech,
            text=text,
            voice=voice,
            output_file=output_file,
            **kwargs
        )
        return await asyncio.get_event_loop().run_in_executor(None, func)