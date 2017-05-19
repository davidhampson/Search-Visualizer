# David Hampson 5/18/2017

import random
from graphics import *
from math import ceil
from tkinter import Tk

## G L O B A L S ## (passed to all methods)
SIZE=0 # data points is SIZE*SIZE
WINSIZE=0 # same as size right now
RESOLUTION=0 # data points per pixel
l=[] # data points
SEARCH=0 # points searched, same as sum of crawler_hist
crawler_hist=[] # searched points by number of searches
minimum=99**99 # lowest value in l
maximum=-99**99  # highest value in l
GLOBALMIN=[0,0,9999999] # mimimum with pos [x,y,v]
BEST=[0,0,99999999] # best found [x,y,v]
####################


def getVal(): # top left cell
    return 0


def getVar(variant): # variant in cells
    return random.normalvariate(0,10)

""" uniform distribution
def getVar(variant):
    return random.uniform(-10,10) + variant # VARIANT (comment out + variant to do without)
"""

class Crawler(): # used for search algo
    def __init__(self, greed, x, y):
        self.x = x
        self.y = y
        self.greed = greed # similar to temperature in SA
        self.value = 0
        
    def update(self):
        global l, SIZE, crawler_hist, SEARCH, BEST
        SEARCH += 1
        # update values
        self.value = l[self.x][self.y]
        if self.value < BEST[2]:
            BEST=[self.x,self.y,self.value]
            
        crawler_hist[self.x][self.y] += 1

        # pick move
        move=random.choice([[1,0],
                            [0,1],
                            [1,1],
                            [-1,0],
                            [0,-1],
                            [-1,1],
                            [1,-1],
                            [-1,-1],
                            ])
        move=move*random.randint(1,50)
        
        lookx = self.x+move[0]
        looky = self.y+move[1]

        # adjust for border
        if lookx >= SIZE-1:
            lookx = SIZE-1
        if looky >= SIZE-1:
            looky = SIZE-1
        if lookx < 0:
            lookx = 0
        if looky < 0:
            looky = 0
            
        # new and old
        n = l[lookx][looky]
        o = self.value

        # SA probability
        if n < o:
            self.x = lookx
            self.y = looky
        elif (2.71828 ** (-(n-o)/self.greed)) < random.uniform(0,1):
            self.x = lookx
            self.y = looky

            
def makeData(): # generate discrete SIZExSIZE floating point array
    global SIZE, WINSIZE, l, SEARCH, GLOBALMIN, BEST, RESOLUTION, \
    crawler_hist, minimum, maximum

    # size
    while True:
        try:
            SIZE=int(input("SIZE(recomended 500): "))
            if SIZE < 1:
                raise
            break
        except:
            print("Positive integers only.")

    WINSIZE=SIZE

    # resolution
    while True:
        try:
            RESOLUTION=int(input("Resolution(recomended 4) \
\n(each pixel represents RESOLUTION*RESOLUTION data points): "))
            
            if RESOLUTION < 1:
                raise
            break
        except:
            print("Positive integers only.")

    # seed
    while True:
        try:
            SEED=input("SEED(blank for random): ")
            if SEED=="":
                SEED=random.random()*100
                
            random.seed(SEED)
            
            print("SEED:",SEED)
            break
        except:
            print("Invalid seed.")

    # create arrays
    print("Creating empty matrix (1 of 2)",end="...")

    for i in range(SIZE):
        row = []
        for i in range(SIZE):
            row.append(0)
        l.append(row)
    print("Done.")


    print("Creating empty matrix (2 of 2)",end="...")

    for i in range(SIZE):
        row = []
        for i in range(SIZE):
            row.append(0)
        crawler_hist.append(row)
    print("Done.")


    # populate
    print("Populating discrete plane",end="...")
    x=0 # progress
    variant=0 # VARIANT
    
    for i in range(SIZE):
        for j in range(SIZE):

            # progress bar
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")
            x+=1

            # top left
            if i == 0 and j == 0:
                l[i][j] = getVal()

            #edges
            if i == 0 and j > 0:
                l[i][j] = l[i][j-1] + getVar(variant)
            if i > 0 and j == 0:
                l[i][j] = l[i-1][j] + getVar(variant)

            # everything else  
            else:
                l[i][j] = ((l[i-1][j] + l[i][j-1])/2 + getVar(variant))


            # stats
            minimum = min(minimum, l[i][j])

            if minimum < GLOBALMIN[2]:
                GLOBALMIN=[i,j,l[i][j]]
                
            maximum = max(maximum, l[i][j])
            
    print("Done.")

# Populates window with data points, returns win object
def makeWin():
    global SIZE, WINSIZE, l, SEARCH, GLOBALMIN, BEST, RESOLUTION, \
    crawler_hist, minimum, maximum

    win = GraphWin("Search-Visualizer",WINSIZE,WINSIZE)

    print("Drawing discrete plane",end="...")
    x=0
    #http://www.science.smith.edu/dftwiki/images/thumb/3/3d/TkInterColorCharts.png/700px-TkInterColorCharts.png
    COLORS_BLUEISH=[
            "SteelBlue1",
            "SteelBlue2",
            "SteelBlue3",
            "SteelBlue4",
            "purple1",
            "purple2",
            "purple3",
            "DarkOrchid3",
            "purple4"]
    
    COLORS_SOLARIZED=[
            "#b58900",
            "#cb4b16",
            "#dc322f",
            "#d33682"]
    
    COLORS_RBGY=["red",
                 "blue",
                 "green",
                 "yellow"]
    
    COLORS_GREY=["#111111",
                 "#222222",
                 "#333333",
                 "#444444",
                 "#555555",
                 "#666666",
                 "#777777",
                 "#888888",
                 "#999999"]

    COLORS_MORDOR=["#000000",
                 "#FF0000",
                 "#555555",
                 "#990033",
                 "#FFCC00",
                 "#FFFF66"]

    COLORS_NEBULA=["#FFFFFF",
                   "#000000",
                   "#FF00FF"]

    
    COLORS=COLORS_MORDOR
    GRADIENT=True
       
    # sort points
    points=[]
    for i in range(SIZE):
        for j in range(SIZE):
            points.append([i,j])
            
    points.sort(key=lambda x: l[x[0]][x[1]])
    
    # Get color codes in dec
    c_CONV=65535/256
    COLORS=list(map(lambda x: [win.winfo_rgb(x)[0]//c_CONV,
                               win.winfo_rgb(x)[1]//c_CONV,
                               win.winfo_rgb(x)[2]//c_CONV],
                    COLORS))
    
    for p in points:
    #for i in range(len(l)):
        #for j in range(len(i[l])):
            i=p[0]
            j=p[1]
            x+=1
            
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")
          
            if i%RESOLUTION==0 and j%RESOLUTION==0:
    
                # color it based on average value of square
                cellVal=l[i][j]
                
                if not RESOLUTION==1:
                    cellVal=0

                    # make sure we don't go off the edge
                    sample=min(SIZE-i-1,SIZE-j-1,RESOLUTION)
                        
                    for q in range(sample):
                        for w in range(sample):
                            cellVal += l[i+q][j+w]

                    cellVal /= sample**2
                    
                # 0 to 1 (doesn't touch 1)
                num=(cellVal-minimum)/(maximum-minimum+0.001)
                
                # num=str(int((l[i][j]-minimum)/((maximum-minimum))*100))[:1]
                
                if not GRADIENT:
                    num *=len(COLORS)
                    color=COLORS[int(num)]
                    
                elif GRADIENT:

                    num *= (len(COLORS)-1)

                    color1=COLORS[int(num)]
                    color2=COLORS[int(num)+1]

                    # components
                    r1=color1[0]
                    r2=color2[0]
                    g1=color1[1]
                    g2=color2[1]
                    b1=color1[2]
                    b2=color2[2]
                    
                    # get ratio, make sure it doesn't touch 256
                    ratio=num-int(num)
                    rN = min(int((1-ratio)*r1 + (ratio)*r2),255) 
                    gN = min(int((1-ratio)*g1 + (ratio)*g2),255)
                    bN = min(int((1-ratio)*b1 + (ratio)*b2),255)

                    color="#{0:02x}{1:02x}{2:02x}".format(rN,gN,bN,2)
                
                if RESOLUTION==1:
                    win.plot(i,j,color)
                    #win.plot(i,j, "#"+num*6)

                else:
                    a = Rectangle(Point(i,j),Point(i+RESOLUTION, j+RESOLUTION))
                    a.setFill(color)
                    a.setOutline(color)
                    # a.setFill("#"+num*6) # shade of gray
                    # a.setOutline("#"+num*6) # shade of gray
                        
                    # draw it
                    a.draw(win)
                    
    print("Done.")
    return win


# Search algorithm, uses global l
def fireworkSearch(win):
    global SIZE, WINSIZE, l, SEARCH, GLOBALMIN, BEST, RESOLUTION, \
    crawler_hist, minimum, maximum
    
    # COLORS
    #   PHASE 1
    #   PHASE 2
    #   PHASE 3
    #   HILL CLIMBER
    #   Final
    #   Best
    #   Global
    COLORS_WHITE=["white",
                  "lemon chiffon",
                  "papaya whip",
                  "old lace",
                  "red",
                  "blue",
                  "yellow"]    
    COLORS_BRIGHT=["white",
                   "yellow",
                   "magenta",
                   "red",
                   "black",
                   "grey",
                   "pink"]
                   
    CRAWLER_COLORS=COLORS_WHITE

    # P H A S E 1
    print("PHASE1")
    phase1=[]

    # DISTRIBUTE X CRAWLERS WITH Y GREED FOR Z STEPS
    X=300
    Y=10
    Z=20
    
    for i in range(X):
        c = Crawler(Y, random.randint(0,SIZE-1), random.randint(0,SIZE-1))
        phase1.append(c)

    # RUN CRAWLERS Z TIMES
    for i in range(Z):
        for c in phase1:
            c.update()
            win.plot(c.x,c.y,CRAWLER_COLORS[0])

    # P H A S E 2
    print("PHASE2") 
    phase2=[]

    # PICK TOP X CRAWLERS, DISTRIBUTE Y CRAWLERS WITH Z GREED AT THEIR LOCATIONS RUNNING Q TIMES
    X=3
    Y=2
    Z=2
    Q=100

    phase1 = sorted(phase1, key=lambda x: x.value)[:X]

    for i in phase1:
        for j in range(Y):
            c = Crawler(Z, i.x, i.y)
            phase2.append(c)

    # RUN CRAWLERS Q TIMES
    for i in range(Q):
        for c in phase2:
            c.update()
            win.plot(c.x,c.y,CRAWLER_COLORS[1])

    # P H A S E 3
    print("PHASE3")
    phase3=[]

    # PICK TOP X CRAWLERS, DISTRIBUTE Y CRAWLERS WITH Z GREED AT THEIR LOCATIONS RUNNING Q TIMES
    X=3
    Y=2
    Z=10
    Q=100

    phase2 = sorted(phase2, key=lambda x: x.value)[:X]

    for i in phase2:
        for j in range(Y):
            c = Crawler(Z, i.x, i.y)
            phase3.append(c)
            
    # RUN CRAWLERS Q TIMES
    for i in range(Q):
        for c in phase3:
            c.update()
            win.plot(c.x,c.y,CRAWLER_COLORS[2])

    print("FINAL PHASE")

    # HILL CLIMBER WITH TOP CLIMBER
    climber = min(phase3, key=lambda x: x.value)
    climber.greed = 1000

    for i in range(500):
        climber.update()
        win.plot(climber.x,climber.y,CRAWLER_COLORS[3])

    print("DONE")

    # Stats
    print("Best Solution Found:",BEST[2],"\nGlobal Minimum:",GLOBALMIN[2])
    if BEST[2] == GLOBALMIN[2]:
        print("GLOBAL MIN FOUND")
    #crawler_hist[climber.x][climber.y] = -1 # mark finish spot

    finish = Circle(Point(climber.x,climber.y),5)
    globalmin = Circle(Point(GLOBALMIN[0],GLOBALMIN[1]),5)
    best = Circle(Point(BEST[0],BEST[1]),5)

    finish.setFill(CRAWLER_COLORS[4])
    globalmin.setFill(CRAWLER_COLORS[5])
    best.setFill(CRAWLER_COLORS[6])

    finish.draw(win)
    globalmin.draw(win)
    best.draw(win)

    print(CRAWLER_COLORS[4].upper(), "DOT: Final crawler endpoint")
    print(CRAWLER_COLORS[5].upper(), "DOT: Best solution found")
    if not BEST[2] == GLOBALMIN[2]: # best covers it
        print(CRAWLER_COLORS[6].upper(), "DOT: Global minimum")

    #for i in range(len(crawler_hist)):
    #    for j in range(len(crawler_hist[i])):
    #        if crawler_hist[i][j] > 3:
    #            win.plot(i,j,"red")
    #        elif crawler_hist[i][j] > 0:
    #            win.plot(i,j,"red3")

    print(SEARCH,"points searched,",str((SEARCH/(SIZE*SIZE))*100)[:3]+"% of points.")

    print("Done.")


# Writes data in csv format
def writeToFile():    

    # WRITE SEARCH SPACE
    file = open("search_domain.csv", 'w')
    x=0
    for i in l:
        for j in i:
            file.write(str(j))
            file.write(",")
            x += 1
        
            if (x%1000 == 0):
                print(str(x/(SIZE*SIZE)*50)+"%")
                
        file.write("\n")
    file.close()

    print("done")

    # WRITE EXPLORATION
    file = open("searched.csv", 'w')
    for i in crawler_hist:
        for j in i:
            file.write(str(j))
            file.write(",")
            x += 1
        
            if (x%1000 == 0):
                print(str(x/(SIZE*SIZE)*50)+"%")
                
        file.write("\n")
    print("done.")

    file.close()

def main():
    makeData()
    fireworkSearch(makeWin())
    input("====INPUT NEWLINE TO EXIT====")

if (__name__) == "__main__":
    main()
