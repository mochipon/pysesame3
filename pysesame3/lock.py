import logging

# For backward compatibility
from pysesame3.chsesame2 import (  # pragma: no cover
    CHSesame2,
    CHSesame2CMD,
    CHSesame2ShadowStatus,
)

logger = logging.getLogger(__name__)
logger.error(
    'This "lock" module is duplecated. Please import "chsesame2" module instead.'
)
