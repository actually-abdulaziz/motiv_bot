import multiprocessing
from motiv_loader_bot import run_loader
from motiv_random_bot import run_viewer

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")  # Решение конфликтов в Linux
    loader = multiprocessing.Process(target=run_loader)
    viewer = multiprocessing.Process(target=run_viewer)
    loader.start()
    viewer.start()
    loader.join()
    viewer.join()