import os
import sys
import marshal
import itertools

import argparse
from operator import itemgetter
from functools import partial
from collections import Counter
import heapq

try:
    import cPickle as pickle
except:
    import pickle

termchar = 17 

#intakes sequence of bytes
#returns tuple with encoded text and decoding ring which is used to decompress the encoded message (enc, decode ring)
def encode(msg):    
     # Count the frequency of each byte in the message
    freq_table = Counter(msg)

    # Build the Huffman tree
    heap = [[weight, [byte, ""]] for byte, weight in freq_table.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    # Generate the Huffman codes
    huff_codes = dict(heapq.heappop(heap)[1:])

    # Create the decoder ring
    decoder_ring = {byte: code for byte, code in huff_codes.items()}

    # Encode the message using the Huffman codes
    encoded_msg = ''.join([huff_codes[byte] for byte in msg])

    return encoded_msg, decoder_ring

#intakes encoded message as well as decoder ring  (outputs of encode) to decode encoded message of 0s and 1s
def decode(cmsg, decoderRing):
    # Creates an array with the appropriate type so that the message can be decoded.
    byteMsg = bytearray()
    current_code = ""
    # Swap the keys and values of the decoder ring
    decoder_ring_swapped = {code: char for char, code in decoderRing.items()}

    for char in cmsg:
        current_code += char
        if current_code in decoder_ring_swapped:
            byte = decoder_ring_swapped[current_code]
            byteMsg.append(byte)
            current_code = ""

    return byteMsg


# This takes a sequence of bytes over which you can iterate, msg, and returns a tuple (compressed, ring) 
# in which compressed is a bytearray (containing the Huffman-coded message in binary, 
# and ring is again the ``decoder ring'' needed to decompress the message.
def compress(msg, useBWT):

    if useBWT:
        msg = bwt(msg)
        msg = mtf(msg)

    # Initializes an array to hold the compressed message.
    compressed = bytearray()
    encoded_str, decoder_ring = encode(msg)
    print(encoded_str)
    extra0 = (len(encoded_str) % 8)
    decoder_ring['extra'] = extra0
    curbin = ''
    for i in range(len(encoded_str)):
        if i % 8 == 0 and (i != 0):
            compressed.append(int(curbin,2))
            curbin = ''
        curbin += encoded_str[i]
        if i == len(encoded_str) - 1:
            compressed.append(int(curbin,2))
    return compressed, decoder_ring


# This takes a sequence of bytes over which you can iterate containing the Huffman-coded message, and the 
# decoder ring needed to decompress it.  It returns the bytearray which is the decompressed message. 
def decompress(msg, decoderRing, useBWT):
    # Creates an array with the appropriate type so that the message can be decoded.
    byteArray = bytearray(msg)
    huf_str = ""
    for i in range(len(byteArray)):
        if (i == len(byteArray) - 1) and (decoderRing['extra'] != 0):
            b_string = '0' + str(decoderRing['extra']) + 'b'
            huf_str += format(int(byteArray[i]),b_string)
            break
        huf_str += format(int(byteArray[i]),'08b')
    decoderRing.pop('extra')
    decompressedMsg = decode(huf_str,decoderRing)

    
    # before you return, you must invert the move-to-front and BWT if applicable
    # here, decompressed message should be the return value from decode()
    if useBWT:
        decompressedMsg = imtf(decompressedMsg)
        decompressedMsg = ibwt(decompressedMsg)

    return decompressedMsg

# memory efficient iBWT
def ibwt(msg):
## Overhead
# - record unique index of each value in BWT
# - sort this indexed list by byte
# - create a dict to map each sorted element to its corresponding element in BWT
  bwt_indexed = [(byte, idx) for idx, byte in enumerate(msg)]
  sorted_bwt_indexed = sorted(bwt_indexed, key=lambda x: x[0])
  mapping = {sorted_bwt_indexed[i]: bwt_indexed[i] for i in range(len(sorted_bwt_indexed))}
  # we start with term character
  og_string = bytearray([17])
  # lets find it in our sorted array
  for i in range(len(sorted_bwt_indexed)):
      if sorted_bwt_indexed[i][0] == 17:
          target_idx = i
          break

  # BACKTRACK 
  # iterate over len of the BWT - 1 to get all characters
  # we know first element in sorted is $
  cur_char = sorted_bwt_indexed[target_idx]
  for i in range(len(msg) - 1):
    # we grab the index of cur_char in the sorted list
    # the element at that index in bwt is the preceding character
    og_string.append(mapping[cur_char][0])
    #og_string.append(msg[sorted_bwt_indexed.index(cur_char)])
    # we now look at the char we just added, but we need its index to correctly locate it in the sorted array, how do we get it?
    # we already have it!!! - sorted_bwt_indexed.index(cur_char)
    # combine these in a tuple and this becomes the new char and its corresponding index
    cur_char = mapping[cur_char]
    #cur_char = (msg[sorted_bwt_indexed.index(cur_char)], sorted_bwt_indexed.index(cur_char))
   
  # the string should be in its original state after termination
  return (og_string[1:])[::-1]


# Burrows-Wheeler Transform fncs
def radix_sort(values, key, step=0):
    sortedvals = []
    radix_stack = []
    radix_stack.append((values, key, step))

    while len(radix_stack) > 0:
        values, key, step = radix_stack.pop()
        if len(values) < 2:
            for value in values:
                sortedvals.append(value)
            continue

        bins = {}
        for value in values:
            bins.setdefault(key(value, step), []).append(value)

        for k in sorted(bins.keys()):
            radix_stack.append((bins[k], key, step + 1))
    return sortedvals
            
# memory efficient BWT
def bwt(msg):
    def bw_key(text, value, step):
        return text[(value + step) % len(text)]

    msg = msg + termchar.to_bytes(1, byteorder='big')

    bwtM = bytearray()

    rs = radix_sort(range(len(msg)), partial(bw_key, msg))
    for i in rs:
        bwtM.append(msg[i - 1])

    return bwtM[::-1]

# move-to-front encoding fncs
def mtf(msg):
    # Initialise the list of characters (i.e. the dictionary)
    dictionary = bytearray(range(256))
    
    # Transformation
    compressed_text = bytearray()
    rank = 0

    # read in each character
    for c in msg:
        rank = dictionary.index(c) # find the rank of the character in the dictionary
        compressed_text.append(rank) # update the encoded text
        
        # update the dictionary
        dictionary.pop(rank)
        dictionary.insert(0, c)

    #dictionary.sort() # sort dictionary
    return compressed_text # Return the encoded text as well as the dictionary

# inverse move-to-front
def imtf(compressed_msg):
    compressed_text = compressed_msg
    dictionary = bytearray(range(256))

    decompressed_img = bytearray()

    # read in each character of the encoded text
    for i in compressed_text:
        # read the rank of the character from dictionary
        decompressed_img.append(dictionary[i])
        
        # update dictionary
        e = dictionary.pop(i)
        dictionary.insert(0, e)
        
    return decompressed_img # Return original string

if __name__=='__main__':

    # argparse is an excellent library for parsing arguments to a python program
    parser = argparse.ArgumentParser(description='Tzip compresses '
                                                 'binary and plain text files using the Burrows-Wheeler transform, '
                                                 'move-to-front coding, and Huffman coding.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', action='store_true', help='Compresses a stream of bytes (e.g. file) into a bytes.')
    group.add_argument('-d', action='store_true', help='Decompresses a compressed file back into the original input')
    group.add_argument('-v', action='store_true', help='Encodes a stream of bytes (e.g. file) into a binary string'
                                                       ' using Huffman encoding.')
    group.add_argument('-w', action='store_true', help='Decodes a Huffman encoded binary string into bytes.')
    parser.add_argument('-i', '--input', help='Input file path', required=True)
    parser.add_argument('-o', '--output', help='Output file path', required=True)
    parser.add_argument('-b', '--binary', help='Use this option if the file is binary and therefore '
                                               'do not want to use the BWT.', action='store_true')

    args = parser.parse_args()

    compressing = args.c
    decompressing = args.d
    encoding = args.v
    decoding = args.w


    infile = args.input
    outfile = args.output
    useBWT = not args.binary

    assert os.path.exists(infile)

    if compressing or encoding:
        fp = open(infile, 'rb')
        sinput = fp.read()
        fp.close()
        if compressing:
            msg, tree = compress(sinput,useBWT)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
        else:
            msg, tree = encode(sinput)
            print(msg)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pck, msg = marshal.load(fp)
        tree = pickle.loads(pck)
        fp.close()
        if decompressing:
            sinput = decompress(msg, tree, useBWT)
        else:
            sinput = decode(msg, tree)
            print(sinput)
        fp = open(outfile, 'wb')
        fp.write(sinput)
        fp.close()