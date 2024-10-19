import sys
import os
import ctypes
from sdl2 import *
from PIL import Image


frames = []
frame_index = 0
fps = 24
window = None
renderer = None
texture = None
scaling_factor = 1.0

# load png with pillow (boilerplate i forgot from where sorry mit license)
def load_frames(frame_folder):
    global frames
    frame_files = sorted([os.path.join(frame_folder, f) for f in os.listdir(frame_folder) if f.endswith('.png')])
    for frame_file in frame_files:
        img = Image.open(frame_file)
        img = img.convert('RGB')  #ensure rgb because the converter is explicit about this
        frames.append(img)

# render for each frame 
def display_frame():
    global frame_index, frames, window, renderer, texture, scaling_factor

    if frame_index < len(frames):
        frame = frames[frame_index]
        frame_data = frame.tobytes("raw", "RGB")
        width, height = frame.size

        # update texture from each png
        SDL_UpdateTexture(texture, None, frame_data, width * 3)
        SDL_RenderClear(renderer)

        # source and destination to fix scale
        src_rect = SDL_Rect(0, 0, width, height)
        dst_rect = SDL_Rect(0, 0, int(width * scaling_factor), int(height * scaling_factor))

        # stick all onto renderer
        SDL_RenderCopy(renderer, texture, src_rect, dst_rect)
        SDL_RenderPresent(renderer)

        frame_index += 1
    else:
        print("End of video.")
        SDL_DestroyRenderer(renderer)
        SDL_DestroyWindow(window)
        SDL_Quit()
        sys.exit(0)
        #this is a bit jank

# define the return and argument types for TIMER_CALLBACK
# the callback needs to return Uint32 and accept Uint32 and a pointer.. idk why but it works :p
TIMER_CALLBACK = ctypes.CFUNCTYPE(Uint32, Uint32, ctypes.c_void_p)

# timer callback controls framerate
@TIMER_CALLBACK
def timer_callback(interval, param): #param?
    display_frame()
    return interval  # return interval to call timer again

# display initialise
def play_video(frame_folder, frame_rate, scale=1.0):
    global fps, window, renderer, texture, scaling_factor
    fps = frame_rate
    scaling_factor = scale

    # frame
    load_frames(frame_folder)

    # sdl2
    SDL_Init(SDL_INIT_VIDEO)
    width, height = frames[0].size

    # scale calc
    scaled_width = int(width * scaling_factor)
    scaled_height = int(height * scaling_factor)

    # window
    window = SDL_CreateWindow(b"video",
                              SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED,
                              scaled_width, scaled_height,
                              SDL_WINDOW_SHOWN)

    # renderer object 
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED)
    texture = SDL_CreateTexture(renderer,
                                SDL_PIXELFORMAT_RGB24,
                                SDL_TEXTUREACCESS_STREAMING,
                                width, height)

    # timer for frame updates
    SDL_AddTimer(int(1000 / fps), timer_callback, None)

    #main lop
    running = True
    while running:
        event = SDL_Event()
        while SDL_PollEvent(event):
            if event.type == SDL_QUIT:
                running = False

    # cleanup
    SDL_DestroyTexture(texture)
    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    SDL_Quit()


if __name__ == "__main__":

    play_video('apple', frame_rate=24, scale=5.0)
