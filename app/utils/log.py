from pathlib import Path
from configs.paths import PT_log_dir

def check_log_dir(func):
    def wrapper(*args, **kwargs):
        log_dir = Path(PT_log_dir)
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        return func(*args, **kwargs)
    return wrapper

def check_log_file(func):
    def wrapper(*args, **kwargs):
        log_file = Path(PT_log_dir) / f"{args[0]}.log"
        if not log_file.exists():
            log_file.touch()
        return func(*args, **kwargs)
    return wrapper

def available_mods(modes):
    def decorator(func):
        def wrapper(*args, **kwargs):
            mode = kwargs.get('mode', None)
            if (mode not in modes) and (mode is not None):
                raise ValueError(f"Modalità {mode} non valida. Le modalità disponibili sono: {modes}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# ------------------------------------------------------------------------------

@check_log_dir
@check_log_file
@available_mods(['a', 'w'])
def log_print(file_stem, message, mode='a', end='\n'):
    with open(Path(PT_log_dir) / Path(f"{file_stem}.log"), mode) as log_file:
        log_file.write(message + end)

@check_log_dir
def log_clear(file_stem):
    with open(Path(PT_log_dir)/f"{file_stem}.log", 'w') as log_file:
        log_file.write("")