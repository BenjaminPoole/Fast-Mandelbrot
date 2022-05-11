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
pygame.display.set_caption('Julia Explorer')

class Julia():
    def __init__(self,x0=0.25,y0=0.0) -> None:
        self.c = x0 + 1.0j * y0 # init at the cusp c=1/4
        self.x = -0.5
        self.y = 0
        self.cmap = plt.cm.jet
        self.false_color = False
        self.radius = 2
        self.escape_time = 0
        self.escape_time_max = 200
        self.size = 500 if DEVICE == 'cuda' else 300
        self.iterations_count = 0 # for window display with count
        self.calculate_matrix()
    
    def calculate_matrix(self):
        '''Create a matrix of complex numbers that we will iterate over to render the set'''
        self.iterations_count = 0 # reset count as we are starting again
        
        x, X, y, Y = self.x-self.radius, self.x+self.radius, self.y-self.radius, self.y+self.radius
        delta = (X-x)/self.size # get length and divide by size to get magnitude of unit step
        re, im = np.mgrid[x:X:delta, y:Y:delta] # we will then step size in total to get from x to X when creating the matrix
        z = (re + 1j*im).reshape(im.shape[0], -1).T # create grid of cooridinates
        
        self.z = torch.tensor(z).to(DEVICE)
        self.escape = torch.zeros_like(torch.abs(self.z)).to(DEVICE)
        self.escape_time = 0
        
    @torch.no_grad()
    def render_julia(self,threshold=4):
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
            torchvision.utils.save_image(torch.tensor(output),f'{self.get_window_name()}, x0={np.real(self.c):.2f}, y0={np.imag(self.c):.2f}, id={random()}.png',normalize=True)
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
        return f'x={self.x}, y={self.y}, x0={np.real(self.c):.2f}, y0={np.imag(self.c):.2f}, radius={self.radius}, res={self.size}, iter={self.iterations_count}, escape_brightness_threshold={self.escape_time_max}'
    
def redrawGameWindow():
    juls.draw(win)
    pygame.display.update()

inital_click = True

juls = Julia()
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        elif event.type == MOUSEWHEEL:
            if event.y > 0:
                radius = juls.radius/2 # make sure that we do not get a divide by zero error. NumPy data structures have limited precision
                if radius > 5e-17:
                    juls.radius /=2
            elif event.y < 0:
               radius = juls.radius*2
               if radius < 1e+300:
                    juls.radius *= 2
            juls.calculate_matrix()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                juls.size -= 100
                if juls.size < 100:
                    juls.size = 100
                juls.calculate_matrix()
            
            if event.key == pygame.K_c:
                juls.false_color = not(juls.false_color) # toggle false color rendering
                
            if event.key == pygame.K_RIGHT:
                juls.size +=100
                # if juls.size > 1000:
                #     juls.size = 1000
                juls.calculate_matrix()
                
            if event.key == pygame.K_DOWN:
                juls.escape_time_max -=20
                juls.calculate_matrix()
                
            if event.key == pygame.K_UP:
                juls.escape_time_max +=20
                juls.calculate_matrix()

            if event.key == pygame.K_s:
                pygame.display.set_caption('Saving image...')
                juls.get_render(save=True)
            
            # Move cursor around julia seed-space (for lack of a better name)
            # Since s is already used I went with Vim (lkjh) move-keys over adws
            if event.key == pygame.K_h:
                juls.c -= 0.02
                juls.calculate_matrix()

            if event.key == pygame.K_l:
                juls.c += 0.02
                juls.calculate_matrix()

            if event.key == pygame.K_j:
                juls.c -= 0.02j
                juls.calculate_matrix()

            if event.key == pygame.K_k:
                juls.c += 0.02j
                juls.calculate_matrix()



    # (left, centre, right) 2E-17
    left_click, _, _ = pygame.mouse.get_pressed()
    
    if left_click: # if left key depressed
        x, y = pygame.mouse.get_rel()
        if inital_click: # if this is the first click rel_pos = 0
            x,y = 0,0
            inital_click = False
            
        juls.x-=juls.radius*x/(WIN_SIZE/5) 
        juls.y-=juls.radius*y/(WIN_SIZE/5)
        juls.calculate_matrix()
        
    else: # if not clicking then the next click will be our first
        inital_click=True

    ## rendering fractal
    for i in range(20):
        juls.render_julia() # every loop keep iterating over the set
        # improving the quality until we recalculate the matrix on user input.

    redrawGameWindow()
pygame.quit()
