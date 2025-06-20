import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

# Create logger
logger = logging.getLogger("hotel_booking_agent")

def log_error(error: Exception, context: dict = None):
    """Log an error with context."""
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" Context: {context}"
    logger.error(error_msg)

def log_info(message: str, context: dict = None):
    """Log an info message with context."""
    info_msg = message
    if context:
        info_msg += f" Context: {context}"
    logger.info(info_msg) 