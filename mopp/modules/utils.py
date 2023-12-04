import shutil
import os
from multiprocessing import Pool
from tqdm import tqdm


def create_folder_without_clear(current_dir):
    if current_dir.exists() and current_dir.is_dir():
        return
    else:
        current_dir.mkdir(parents=True, exist_ok=True)
        
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





def pool_processes(num_processes, function_list):
    with Pool(processes=num_processes) as pool:
        for func in function_list:
            pool.map_async(func[0], func[1])
        pool.close()
        pool.join()

def get_directory_size(directory_path):
    total_size = 0
    try:
        with os.scandir(directory_path) as entries:
            for entry in entries:
                if entry.is_file():
                    total_size += entry.stat().st_size
                elif entry.is_dir():
                    total_size += get_directory_size(entry.path)
        return total_size
    except FileNotFoundError:
        return None
    
def convert_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0


def get_available_storage(path="/"):
    try:
        total, used, free = shutil.disk_usage(path)
        return free
    except FileNotFoundError:
        return None
    
def check_storage(input, multiplier=2):
    input_size = get_directory_size(input)
    available_space = get_available_storage()

    ideal_space = input_size * multiplier

    if ideal_space > available_space:
        return convert_size(-(available_space-ideal_space))
    else:
        return 1


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
