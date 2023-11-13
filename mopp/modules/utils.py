import shutil


def clear_folder(current_dir):
    for item in current_dir.iterdir():
        if item.is_file():
            item.unlink()
        if item.is_dir():
            shutil.rmtree(item)
