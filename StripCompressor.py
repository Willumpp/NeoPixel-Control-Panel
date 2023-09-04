from settings import *
import numpy as np

class StripCompressorNumpy:
    def __init__(self, pixel_count):
        self.pixel_count = pixel_count


    def compress_numpy_strip(self, inp_array):

        out = np.zeros((self.pixel_count*4 + 1, ), dtype=np.uint16)
        count = 1
        last_item = inp_array[0]
        compression_count = 0

        _size = len(inp_array)
        _pointer = 1

        for item_i in range(1, _size):
            item = inp_array[item_i]

            if np.array_equal(item, last_item):
                count += 1
            else:
                # out.append([count, last_item])
                out[_pointer] = count
                out[_pointer+1] = last_item[0]
                out[_pointer+2] = last_item[1]
                out[_pointer+3] = last_item[2]

                count = 1
                compression_count += 1
                _pointer += 4

            last_item = inp_array[item_i]


        out[_pointer] = count
        out[_pointer+1] = last_item[0]
        out[_pointer+2] = last_item[1]
        out[_pointer+3] = last_item[2]
        out[0] = compression_count+1
        
        return out[:(compression_count*4)+5]


    def uncompress_numpy_strip(self, compressed_strip, output_shape):

        out = np.zeros(output_shape)
        total = 0

        for item_i in range(1, len(compressed_strip), 4):
            count = compressed_strip[item_i]
            r = compressed_strip[item_i+1]
            g = compressed_strip[item_i+2]
            b = compressed_strip[item_i+3]

            out[total:total+count] = np.array([r, g, b], dtype=np.uint16)
            total += count

        return out

    def serialise_strip(self, inp_array):
        compressed = self.compress_numpy_strip(inp_array)

        return compressed.tobytes()



    def serialise_strip_2(self, inp_array):
        flattened = inp_array.flatten()

        return flattened.tobytes()

    def break_packets_2(self, packets):
        packets = self.from_buffer(packets)

        for packet_i in range(0, len(packets), self.pixel_count*3):

            packet = packets[packet_i:packet_i+self.pixel_count*3]

            packet.shape = (self.pixel_count, 3)
            yield packet

    def deserialise_strip_2(self, bytes_array):

        from_buffer = np.frombuffer(bytes_array, dtype=np.uint16)
        from_buffer.shape = (self.pixel_count, 3)

        return from_buffer


    def deserialise_strip(self, bytes_array):
        from_buffer = np.frombuffer(bytes_array, dtype=np.uint16)


        uncompressed = self.uncompress_numpy_strip(from_buffer, (self.pixel_count,3))
        return uncompressed


    def from_buffer(self, bytes_array):
        return np.frombuffer(bytes_array, dtype=np.uint16)


    def break_packets(self, packets):
        i = 0
        while i < len(packets):
            count = packets[i]

            #First index of each packet is the number of compressions which were made
            packet = packets[i:i+count*4 + 1]

            yield self.uncompress_numpy_strip(packet, (self.pixel_count, 3))

            if count*4 + 1 >= len(packets): break

            i += packets[count*4 + 1]*4 + 1


class StripCompressor:
    def __init__(self, pixel_count):
        self.pixel_count = pixel_count

    #inp_array must be a numpy array
    def serialise_strip_from_numpy(self, inp_array):
        flattened = inp_array.flatten()

        return bytes(list(flattened))

    #Bytes must be a regular python list with ints (as bytes)
    def deserialise_strip(self, bytes):
        return list(bytes)

    #inp_array must be a flattened python list of the strip pixels
    def reshape(self, inp_array):
        if len(inp_array) != PIXEL_COUNT*3: raise Exception("INCORRECT INP ARRAY SIZE")
        out = []

        for i in range(0, PIXEL_COUNT*3, 3):

            _line = [0, 0, 0]
            for j in range(0, 3):
                _line[j] = inp_array[i+j]
            out.append(_line)

        return out

    #packets must be serialised
    def break_packets(self, packets):
        packets = self.deserialise_strip(packets)

        for packet_i in range(0, len(packets), self.pixel_count*3):

            packet = packets[packet_i:packet_i+self.pixel_count*3]

            yield self.reshape(packet)

            




def test_sample():
    import random

    out = []

    while len(out) < PIXEL_COUNT:
        count = random.randint(1, 10)

        _temp = [random.randint(0, 255) for j in range(3)]
        for i in range(count):
            out.append(_temp)

        
    return np.array(out)[:PIXEL_COUNT]

        

if __name__ == "__main__":

    compressor = StripCompressor(PIXEL_COUNT)

    _sample = test_sample()

    print(_sample)

    bytes = compressor.serialise_strip_from_numpy(_sample) + compressor.serialise_strip_from_numpy(_sample)

    for packet in compressor.break_packets(bytes):
        print(packet)


