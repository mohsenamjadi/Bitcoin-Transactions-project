import bitcoin
import random
import time
import sys
from multiprocessing import Process, Value

THREADS = 16

class vanitygen(Process):
    def _init_ (self, pattern):
        Process._init_(self)
        self.pattern = pattern

    def run(self):
        while 1:
            # generate the secret private key
            secret_key = bitcoin.random_key()

            # generate the address derived from private key
            address = bitcoin.privkey_to_address(secret_key)

            if address.startswith("1" + self.pattern): break

        print("Vanity address found: ", address)
        print("HEX private key: ", secret_key)

def pattern_mine():
    #Init worker threads
    workers = []
    for i in range(0,THREADS):
        worker = vanitygen("moh")
        worker.daemon = True
        workers.append(worker)
        worker.start()

start = time.time()
pattern_mine()
end = time.time() - start
print("Elapsed time: ", end)