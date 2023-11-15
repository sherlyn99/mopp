import shutil
import subprocess


def create_folder(current_dir):
    if current_dir.exists() and current_dir.is_dir():
        clear_folder(current_dir)
    else:
        current_dir.mkdir(parents=True, exist_ok=True)


def clear_folder(current_dir):
    for item in current_dir.iterdir():
        if item.is_file():
            item.unlink()
        if item.is_dir():
            shutil.rmtree(item)


# import time
# import logging

# logger = logging.getLogger("modules")
# logger.setLevel(logging.INFO)

# timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
# formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")

# filer_handler = logging.FileHandler(f"modules_{timestamp}.log")
# filer_handler.setFormatter(formatter)
# logger.addHandler(filer_handler)

# stream_handler = logging.StreamHandler()
# stream_handler.setFormatter(formatter)
# logger.addHandler(stream_handler)
