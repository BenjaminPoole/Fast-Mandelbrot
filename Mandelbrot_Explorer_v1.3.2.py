import pygame
from pygame.locals import *
import torch
import torchvision
import numpy as np
import matplotlib.pyplot as plt
from random import random

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
pygame.init()

WIN_SIZE = 1000
win = pygame.display.set_mode((WIN_SIZE,WIN_SIZE))
pygame.display.set_caption('Mandelbrot Explorer')

class Mandelbrot():
    def __init__(self) -> None:
        self.x = -0.5
        self.y = 0
        self.cmap = plt.cm.jet
        self.false_color = False
        self.radius = 2
        self.escape_time = 0
        self.escape_time_max = 200
        self.size = 500 if DEVICE == 'cuda' else 100
        self.iterations_count = 0 # for window display with count
        self.calculate_matrix()
    
    def calculate_matrix(self):
        '''Create a matrix of complex numbers that we will iterate over to render the set'''
        self.iterations_count = 0 # reset count as we are starting again
        
        x, X, y, Y = self.x-self.radius, self.x+self.radius, self.y-self.radius, self.y+self.radius
        delta = (X-x)/self.size # get length and divide by size to get magnitude of unit step
        re, im = np.mgrid[x:X:delta, y:Y:delta] # we will then step size in total to get from x to X when creating the matrix
        c = (re + 1j*im).reshape(im.shape[0], -1).T # create grid of cooridinates
        
        self.c = torch.tensor(c).to(DEVICE)
        self.z = torch.zeros_like(self.c).to(DEVICE)
        self.escape = torch.zeros_like(torch.abs(self.c)).to(DEVICE)
        self.escape_time = 0
        
    @torch.no_grad()
    def render_mandelbrot(self,threshold=4):
        self.iterations_count += 1
        if self.escape_time < self.escape_time_max:
            self.escape_time +=1
            
        old_z = self.z
        self.z = self.z*self.z + self.c # element-wise multiplication
        idx = (torch.abs(self.z) > threshold) & (self.escape == 0) # if diverges then measure the rate of change of divergence. 
        self.escape[idx] = torch.abs(self.z-old_z)[idx]+self.escape_time# = 0/(num_iter/50) # Only do this once when it has escaped otherwise its tends to infinity hence (escape==0) condition

    def get_render(self,save=False):
        output = self.escape.detach().cpu().numpy()# + self.escape_time
        output = 255*output/np.max(output) # normalize between 0-255
        if save:
            torchvision.utils.save_image(torch.tensor(output),f'{self.get_window_name()}, id={random()}.png',normalize=True)
        return output
    
    def convert_2_gray(self,im):
        # im = 255 * (im / im.max())
        w, h = im.shape
        ret = np.empty((w, h, 3), dtype=np.uint8)
        ret[:, :, 2] = ret[:, :, 1] = ret[:, :, 0] = im
        return ret
    
    def draw(self,win):
        output = self.get_render().T
        if self.false_color:
            output = self.cmap(output/255)*255
            output = output[:,:,:-1]

        else:
            output = self.convert_2_gray(output)
        
        output = pygame.surfarray.make_surface(output)
        output = pygame.transform.scale(output,(WIN_SIZE,WIN_SIZE))
        win.blit(output,(0,0))
        
        pygame.display.set_caption(self.get_window_name())

    def get_window_name(self):
        return f'x={self.x}, y={self.y}, radius={self.radius}, res={self.size}, iter={self.iterations_count}, escape_brightness_threshold={self.escape_time_max}'
    
def redrawGameWindow():
    mbs.draw(win)
    pygame.display.update()

inital_click = True

mbs = Mandelbrot()
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        elif event.type == MOUSEWHEEL:
            if event.y > 0:
                radius = mbs.radius/2 # make sure that we do not get a divide by zero error. NumPy data structures have limited precision
                if radius > 5e-17:
                    mbs.radius /=2
            elif event.y < 0:
               radius = mbs.radius*2
               if radius < 1e+300:
                    mbs.radius *= 2
            mbs.calculate_matrix()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                mbs.size -= 100
                if mbs.size < 100:
                    mbs.size = 100
                mbs.calculate_matrix()
            
            if event.key == pygame.K_c:
                mbs.false_color = not(mbs.false_color) # toggle false color rendering
                
            if event.key == pygame.K_RIGHT:
                mbs.size +=100
                # if mbs.size > 1000:
                #     mbs.size = 1000
                mbs.calculate_matrix()
                
            if event.key == pygame.K_DOWN:
                mbs.escape_time_max -=20
                mbs.calculate_matrix()
                
            if event.key == pygame.K_UP:
                mbs.escape_time_max +=20
                mbs.calculate_matrix()

            if event.key == pygame.K_s:
                pygame.display.set_caption('Saving image...')
                mbs.get_render(save=True)
            

    # (left, centre, right) 2E-17
    left_click, _, _ = pygame.mouse.get_pressed()
    
    if left_click: # if left key depressed
        x, y = pygame.mouse.get_rel()
        if inital_click: # if this is the first click rel_pos = 0
            x,y = 0,0
            inital_click = False
            
        mbs.x-=mbs.radius*x/(WIN_SIZE/5) 
        mbs.y-=mbs.radius*y/(WIN_SIZE/5)
        mbs.calculate_matrix()
        
    else: # if not clicking then the next click will be our first
        inital_click=True

    ## rendering fractal
    for i in range(20):
        mbs.render_mandelbrot() # every loop keep iterating over the set
        # improving the quality until we recalculate the matrix on user input.

    redrawGameWindow()
pygame.quit()