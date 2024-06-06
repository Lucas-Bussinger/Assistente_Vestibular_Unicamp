import time
import portalocker


#funções de comunicação entre o site e o chatbot
def ler(path):
    
    try:
        with open(path, 'r', encoding= 'utf-8') as file:
            portalocker.lock(file, portalocker.LOCK_SH)
            data = file.read()
            portalocker.unlock(file)
            return data
    except portalocker.LockException:
        time.sleep(0.05)
        return ler(path)

def escrever(path, message):
    try:
        with open(path, 'w', encoding= 'utf-8') as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            file.write(message)
            portalocker.unlock(file)
    
    except portalocker.LockException:
        time.sleep(0.05)
        escrever(path, message)