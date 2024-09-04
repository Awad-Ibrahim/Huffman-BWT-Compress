import bwt_huffman
from gzip import compress, decompress
import time
from matplotlib import pyplot as plt


def time_complexity():
    pass

def compression_ratio():
    pass

start = time.time()
with open('textfile.txt', 'rb') as f: txt = f.read()
encode = compress(txt)
with open('encoded1.txt','wb') as f: f.write(encode)
decode = decompress(encode)
with open('output1.txt', 'wb') as f: f.write(decode)
end = time.time()

print(f"gzip runtime = {end - start}")



start = time.time()
with open('textfile.txt', 'rb') as f: txt = f.read()
encode, decoder_ring = bwt_huffman.compress(txt, True)
with open('encoded2.txt','wb') as f: f.write(encode)
decode = bwt_huffman.decompress(encode, decoder_ring, True)
with open('output2.txt', 'wb') as f: f.write(decode)
end = time.time()

print(f"bzip2 runtime = {end - start}")