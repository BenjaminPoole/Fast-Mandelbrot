# Fast-Mandelbrot
![Mandelbrot demo](https://user-images.githubusercontent.com/86885371/151717624-7b03822b-3f3b-431f-9d72-5c1f7f67354c.jpg)
An iteractive GPU-accelerated and cross platform Mandelbrot set explorer built in python.

## Usage
It is recommeded to run this program with a GPU as rendering is very much faster.
1. Clone the repository and run `Mandelbrot_Explorer_v1.3.2.py`.
2. Click and drag to move around. Scroll with mouse to zoom.
3. Use left and right arrow keys to change resolution. Lower res = faster renders.
4. Use `up`and `down` arrow keys to change escape threshold. When you zoom in you will probably need to increase this value because you are computing more iterations.
5. Press `c` to toggle false color which by default is grayscale (saves will always be grayscale even with false color).
6. Press `s` to save image of render on screen. This will save the image as a png to either your home directory or current working directory depending on your OS. 

The image filename will contain the coordinates of where you are in the Mandelbrot set etc to enable reproducible results.
The top bar of the program also shows coordinates of where you are as well as the resolution and escape brightness.

## How it works
1. At every iteration the program creates a matrix `z` of all the coordinates in the image it wants to render. By using a matrix of complex numbers instead of iterating scalar values this allows the computation to be parallelized and thus enables GPU computation for maximum render speed.
2. The iterative formula `Z = Z^2 + c` is then applied every iteration.  To render the set the program measures how many iterations it takes for a given value of `c` to diverge (magnitude > 4) and that pixel is assigned a corresponding brightness where the upper limit of the brightness is set by the escape threshold. Next the gradient of its value w.r.t the last iteration is computed and that pixel is assigned a brightness corresponding to the magnitude of the gradient.

#### Dependancies
* Python 3 with pytorch, pygame, matplotlib and numpy installed. Make sure to install the GPU version of pytorch if you have a GPU.
This program has been tested on both Windows 10 and Linux.

#### Credits
This program was based on [this notebook](https://github.com/mnd-af/src/blob/master/2020/07/14/Mandelbrot.ipynb) and the corresponding [Youtube video](https://youtu.be/GvVYKoX1g2s) which taught the author how to do this.

If you wish to ask questions/report a bug or contribute then make sure to open an issue and let me know.
