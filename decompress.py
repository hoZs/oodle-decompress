import array
import ctypes
import decimal
from os import path
import struct
import os
import platform
import glob




class Decompresser:

    def __init__(self):
        operatingSystem: str = platform.system()

        try:
            if operatingSystem == 'Windows':
                self.oodle = ctypes.CDLL('./oo2core_9_win64.dll')
            elif operatingSystem == 'Linux':
                self.oodle = ctypes.CDLL('./liboo2corelinux64.so.9')
        except FileNotFoundError:
            print("Error: oo2core file not found")
            exit()

        self.oodle.OodleLZ_Decompress.argtypes = [
            ctypes.c_char_p,  # compBuf
            ctypes.c_size_t,  # compBufSize
            ctypes.c_char_p,  # rawBuf
            ctypes.c_size_t,  # rawBufSize
            ctypes.c_int,     # fuzzSafe
            ctypes.c_int,     # checkCRC
            ctypes.c_int,     # verbosity
            ctypes.c_void_p,  # decBufBase
            ctypes.c_size_t,  # decBufSize
            ctypes.c_void_p,  # fpCallback
            ctypes.c_void_p,  # callbackUserData
            ctypes.c_void_p,  # decoderMemory
            ctypes.c_size_t,  # decoderMemorySize
            ctypes.c_int      # threadPhase
        ]
        self.oodle.OodleLZ_Decompress.restype = ctypes.c_int

    def _open_file(self, fileAddr = None):
        if fileAddr == None:
            fileAddr = self._first_sav_file()
        with open(fileAddr, 'rb') as file:
            data: bytes = file.read()
        return data
    
    def main_process(self, saveToDisk: bool = False, filePath: str = None):
        data = self._open_file(filePath)

        uncompressedSize: int = self._calculate_size(data)
        compressedData: bytes = data[4:]
        compressedSize: int = len(compressedData)


        decompressedBuffer = ctypes.create_string_buffer(uncompressedSize)

        result = self._decompress(compressedData, compressedSize, decompressedBuffer, uncompressedSize)
        print(result)
        if saveToDisk:
            self._write_bin(result, decompressedBuffer)
            return None
        elif result > 0:    
            return decompressedBuffer 
        else:
            print("Error: faulty conversion")
            return None

    def _write_bin(self, result, decompressedBuffer):
        if result > 0:
            os.makedirs('output', exist_ok=True)
            outPath = os.path.join('output', 'decoded_save_data.bin')
            with open(outPath, 'wb') as outFile:
                outFile.write(decompressedBuffer.raw)
            print("Success")
        else:
            print("Failure")

    def _decompress(self, compressedData: bytes, compressedSize: int, decompressedBuffer: bytes, uncompressedSize: int):
        result = self.oodle.OodleLZ_Decompress(
            compressedData,            # compBuf
            compressedSize,            # compBufSize
            decompressedBuffer,        # rawBuf
            uncompressedSize,          # rawBufSize
            1,                          # fuzzSafe (1 = safe)
            0,                          # checkCRC
            0,                          # verbosity
            None,                       # decBufBase
            0,                          # decBufSize
            None,                       # fpCallback
            None,                       # callbackUserData
            None,                       # decoderMemory
            0,                          # decoderMemorySize
            0                           # threadPhase
        )
        return result
    
    def _calculate_size(self, data: bytes) -> int:
        uncompressedSize = struct.unpack('<I', data[0:4])[0]
        return uncompressedSize

    def _first_sav_file(self) -> str:
        pattern = os.path.join('sav', '*.sav')
        files = glob.glob(pattern)
        if files: 
            return files[0] 
        else:
            print("No .sav files were found.")
            exit()

if __name__ == '__main__':
    decomp = Decompresser()
    decomp.main_process(saveToDisk=True)