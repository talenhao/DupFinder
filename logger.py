import os
import logging
from logging.handlers import TimedRotatingFileHandler


def configure_logger(log_file_name=__name__):
    # 创建一个logger对象
    logger = logging.getLogger(__name__)

    # 检查是否已经配置过日志记录器
    if not logger.hasHandlers():
        # 设置日志级别
        logger.setLevel(logging.DEBUG)

        # 创建一个控制台处理器并设置级别为DEBUG
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建一个文件处理器并设置级别为DEBUG
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)  # 确保logs目录存在
        log_file_path = os.path.join(logs_dir, f'{log_file_name}.log')

        # 创建 TimedRotatingFileHandler 实例
        handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=7)
        handler.setLevel(logging.DEBUG)

        # 创建一个格式化器并将其添加到处理器
        # 创建日志格式化对象
        log_format_attributes = [
            '%(asctime)s',
            '%(levelname)s',
            '%(filename)s',
            'line:%(lineno)d',
            '%(funcName)s', 
            # '%(process)d:',
            # '%(processName)s',
            '%(message)s',
        ]
        log_format_string = " - ".join(log_format_attributes)
        format = logging.Formatter(fmt=log_format_string)  # 日志格式

        console_handler.setFormatter(format)
        handler.setFormatter(format)

        # 将处理器添加到logger对象
        logger.addHandler(console_handler)
        logger.addHandler(handler)

    return logger


# # 示例调用
# if __name__ == "__main__":
#     log_file_name = 'app'  # 日志文件名参数
#     logger = configure_logger(log_file_name)
#     logger.info("This is an info message")
#     logger.debug("This is a debug message")