import subprocess
import sys

if __name__ == "__main__":
    # Запуск ботов в отдельных процессах с изоляцией
    process_loader = subprocess.Popen([sys.executable, "motiv_loader_bot.py"])
    process_viewer = subprocess.Popen([sys.executable, "motiv_random_bot.py"])
    
    process_loader.wait()
    process_viewer.wait()