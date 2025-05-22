import multiprocessing
from motiv_loader_bot import run_loader
from motiv_random_bot import run_viewer

if __name__ == "__main__":
    # Явно указываем запуск через spawn (для совместимости)
    multiprocessing.set_start_method("spawn")
    
    loader_process = multiprocessing.Process(target=run_loader)
    viewer_process = multiprocessing.Process(target=run_viewer)
    
    loader_process.start()
    viewer_process.start()
    
    loader_process.join()
    viewer_process.join()