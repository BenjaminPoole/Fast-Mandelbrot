# Fast-Mandelbrot
![Mandelbrot demo](https://user-images.githubusercontent.com/86885371/151717624-7b03822b-3f3b-431f-9d72-5c1f7f67354c.jpg)
An iteractive GPU-accelerated Mandelbrot set explorer built in python.

## Usage
It is recommeded to run this program with a GPU as rendering is very much faster
1. Clone the repository and run mandelbrot.py
2. Click and drag to move around. Scroll with mouse to zoom
3. Use left and right arrow keys to change resolution. Lower res = faster renders
4. Use `up`and `down` arrow keys to change escape brightness.
5. Press `c` to toggle false color
6. Press `s` to save image of render on screen. This will save the image as a png to either your home directory or current working directory depending on your OS. 

The image filename will contain the coordinates of where you are in the Mandelbrot set etc to enable reproducible results.
The top bar of the program also shows coordinates of where you are as well as the resolution and escape brightness.

If you wish to ask questions/report a bug or contribute then make sure to open an issue and let me know.

#### Dependancies
Python 3 with pytorch and pygame installed. Make sure to install the GPU version of pytorch if you have a GPU.
