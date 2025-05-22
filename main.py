import subprocess

if __name__ == "__main__":
    # Запуск ботов в отдельных процессах
    subprocess.Popen(["python", "motiv_loader_bot.py"], stdout=subprocess.PIPE)
    subprocess.Popen(["python", "motiv_random_bot.py"], stdout=subprocess.PIPE)
    # Бесконечное ожидание
    while True:
        pass