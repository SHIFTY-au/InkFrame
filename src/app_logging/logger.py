import logging
import os
import logging.handlers

def setup_logging(log_file='logs/app.log'):
    # Ensure log directory exists before creating FileHandler
    os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)

    logger = logging.getLogger('inkFrame')
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # use rotating file handler for production
    file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger

if __name__ == '__main__':
    setup_logging()
    logger = logging.getLogger('inkFrame')
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")