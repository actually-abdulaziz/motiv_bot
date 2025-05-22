import threading
from motiv_loader_bot import run_loader
from motiv_random_bot import run_viewer

if __name__ == "__main__":
    # Запуск ботов в отдельных потоках с явным указанием event loop
    loader_thread = threading.Thread(target=run_loader)
    viewer_thread = threading.Thread(target=run_viewer)
    
    loader_thread.start()
    viewer_thread.start()
    
    loader_thread.join()
    viewer_thread.join()