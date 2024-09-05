This project implements a data compression algorithm utilizing a combination of Huffman coding, Burrows-Wheeler Transform (BWT), and Move-to-Front (MTF) encoding in Python. 
The project also includes a benchmarking file which can be used to test functionality (a .txt file has been provided) as well as compare its performance against other forms of compression.

## Features
- Compression algorithm combining Huffman coding, BWT, and MTF.
- Memory-efficient implementations of BWT and inverse BWT
- Option to compress files with or without BWT if higher efficiency/lower compression is desired
- Benchmarking tool for performance comparison and analysis

## How it Works ##

  ### Compression Process:

1. Burrows-Wheeler Transform (BWT):
   - Rearranges the input data to group similar characters together.
   - This transformation makes the data more compressible by creating runs of similar characters.

2. Move-to-Front (MTF) encoding:
   - Converts local repetitions in the BWT output into smaller values.
   - This step helps to represent frequent characters with smaller numbers, which are easier to compress.

3. Huffman coding:
   - Analyzes the frequency of symbols.
   - utilizes a heap to build a Huffman Tree
   - Assigns shorter binary codes to more frequent symbols and longer codes to less frequent ones
   - This variable-length encoding results in overall data compression.

  ### Decompression Process:
  
1. Huffman decoding:
   - Uses the decoder ring to convert the Huffman-coded data back into its pre-Huffman form.

2. Inverse Move-to-Front (IMTF):
   - Reverses the MTF encoding, reconstructing the original character sequences.

3. Inverse Burrows-Wheeler Transform (IBWT):
   - Transforms the data back to its original order before BWT was applied.

  ### Additional Features:

- Binary file handling: For binary files, the BWT step can be optionally skipped to preserve exact byte values.
- Flexible encoding/decoding: The `encode` and `decode` functions provide lower-level access to just the Huffman coding step, useful for custom implementations or testing.

## Benchmarking
- benchmark.py allows user to test the compression ratio as well as speed in comparison with other methods of compression ex. Gzip
