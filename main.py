import threading
from motiv_loader_bot import run_loader
from motiv_random_bot import run_viewer

if __name__ == "__main__":
    loader_thread = threading.Thread(target=run_loader, name="LoaderThread")
    viewer_thread = threading.Thread(target=run_viewer, name="ViewerThread")
    
    loader_thread.start()
    viewer_thread.start()
    
    loader_thread.join()
    viewer_thread.join()
