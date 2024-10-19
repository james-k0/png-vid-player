import struct
import zlib
import time
import os

# for terminal
def rgb_to_ascii(r, g, b):
    grayscale = int((r + g + b) / 3)
    if grayscale < 64:
        return '█' 
    elif grayscale < 128:
        return '▓'
    elif grayscale < 192:
        return '▒'
    else:
        return '░' 

# parse png
def read_png(filename):
    with open(filename, 'rb') as f:
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            raise ValueError("Not a valid PNG file")

        chunks = []
        while True:
            length = struct.unpack('>I', f.read(4))[0]
            chunk_type = f.read(4)
            chunk_data = f.read(length)
            crc = f.read(4)  # ignore crc

            chunks.append((chunk_type, chunk_data))
            if chunk_type == b'IEND':
                break

    #IHDR chunk to describe w,h,depth, colr
    for chunk_type, chunk_data in chunks:
        if chunk_type == b'IHDR':
            width, height, bit_depth, color_type = struct.unpack('>IIBB', chunk_data[:10])
            if bit_depth not in [8, 16]:
                raise ValueError("This script supports bit depth 8 or 16 PNGs.")
            break

    #extract and decompress IDAT chunks 
    idat_data = b''.join(chunk_data for chunk_type, chunk_data in chunks if chunk_type == b'IDAT')
    decompressed_data = zlib.decompress(idat_data)

    #process decompressed img assuming RGB
    pixels = []
    idx = 0
    bytes_per_pixel = 3 if bit_depth == 8 else 6  # 3byte:8bit chan, 6byte:16bit chan

    for y in range(height):
        filter_type = decompressed_data[idx]  # filter type (ignore)
        idx += 1
        row = []
        for x in range(width):
            if bit_depth == 8:
                r = decompressed_data[idx]
                g = decompressed_data[idx + 1]
                b = decompressed_data[idx + 2]
                idx += 3
            elif bit_depth == 16:
                r = struct.unpack('>H', decompressed_data[idx:idx + 2])[0] // 256  # normalise to 8bit
                g = struct.unpack('>H', decompressed_data[idx + 2:idx + 4])[0] // 256
                b = struct.unpack('>H', decompressed_data[idx + 4:idx + 6])[0] // 256
                idx += 6
            row.append((r, g, b))
        pixels.append(row)

    return width, height, pixels

def render_image(width, height, pixels):
    for y in range(height):
        line = ''.join(rgb_to_ascii(*pixels[y][x]) for x in range(width))
        print(line)

def play_video(frame_folder, fps=24):
    import os
    frames = sorted([os.path.join(frame_folder, f) for f in os.listdir(frame_folder) if f.endswith('.png')])

    current_fps = fps
    for frame_file in frames:
        # print(f"Displaying: {frame_file}")
        width, height, pixels = read_png(frame_file)
        render_image(width, height, pixels)
        
        # timing control
        time.sleep(1 / current_fps)
        # print("\033c", end='')  # clear screen (console)
        os.system('cls') #both of these options suck. but its console print so will
        #always be bad its printing to command line. maybe i test in xterm or smth xd
        
play_video('apple', fps=60)
