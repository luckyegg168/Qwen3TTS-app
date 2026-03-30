"""API client exceptions"""


class APIError(Exception):
    """Base exception for API errors"""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class VoiceCloneError(APIError):
    """Exception raised when voice cloning fails"""

    pass


class TTSError(APIError):
    """Exception raised when TTS synthesis fails"""

    pass
