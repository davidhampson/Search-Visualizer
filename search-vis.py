# David Hampson 5/18/2017
# TODO: make winsize a feature


import random
from graphics import *
from tkinter import Tk

## G L O B A L S ## (passed to all methods)

    ## WINDOW STUFF
SIZE=0 # data points is SIZE*SIZE
WINSIZE=0 # same as size right now
RESOLUTION=0 # data points per pixel
    #########

    ## DISCRETE PLANE
l=[] # data points
    #########

    ## STATS
SEARCH=0 # points searched, same as sum of crawler_hist
crawler_hist=[] # searched points by number of searches
minimum=0 # lowest value in l
maximum=0  # highest value in l
GLOBALMIN=[0,0,0] # mimimum with pos [x,y,v]
BEST=[0,0,99**99] # best found [x,y,v]
    ########

####################


def getVal(): # top left cell
    return random.uniform(-10,10)

def getVar(): #uniform distribution
    #return random.normalvariate(0,10)
    return random.uniform(-10,10)

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

    if not WINSIZE:
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
                SEED=int(random.random()*1000000)
                
            random.seed(SEED)
            
            print("SEED:",SEED)
            break
        except:
            print("Invalid seed.")

    # create arrays
    
    print("Creating empty matrices",end="...")
    num_of_planes=0

    l1=[] # W->E
    l2=[] # NW->SE
    l3=[] # N->S
    l4=[] # NE->SW
    
    PLANES=[l1,l2,l3,l4]
    y=0 # count how many we have drawn

    for i in range(SIZE):
        row = []
        for i in range(SIZE):
            row.append(0)
        l.append(row[:])
        for p in PLANES:
            p.append(row[:])
        crawler_hist.append(row[:])
    print("Done.")


    # populate
    x=0 # progress
    
    #l1
    for i in range(SIZE):
        if i==0:
            if not l1 in PLANES:
                break
            y+=1
            print("\nPopulating discrete plane("+str(y)+"/"+str(len(PLANES))+")",end="...")

        for j in range(SIZE):

            # progress bar
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")
            x+=1


            # top corner
            if i == 0 and j == 0:
                l1[i][j] = getVal()

            # top row
            elif j > 0 and i == 0:
                l1[i][j] = l1[i][j-1] + getVar()
            else:
                if j < SIZE-1: 
                    #l[i][j] = (l[i-1][j-1] + l[i-1][j] + l[i-1][j+1] + l[i][j-1])/4 + getVar() #include influence from left
                    l1[i][j] = (l1[i-1][j-1] + l1[i-1][j] + l1[i-1][j+1])/3 + getVar()

                elif j == SIZE-1: # wrap around on right edge (0 does it for us with -1)
                    l1[i][j] = (l1[i-1][j-1] + l1[i-1][j] + l1[i-1][0])/3 + getVar()


    #l2
    for i in range(SIZE):
        if i==0:
            if not l2 in PLANES:
                break
            y+=1
            print("\nPopulating discrete plane("+str(y)+"/"+str(len(PLANES))+")",end="...")
            x=0

        for j in range(SIZE):

            # progress bar
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")
            x+=1

            # top corner
            if i == 0 and j == 0:
                l2[i][j] = getVal()

            #edges
            elif i == 0 and j > 0:
                l2[i][j] = l2[i][j-1] + getVar()
            elif i > 0 and j == 0:
                l2[i][j] = l2[i-1][j] + getVar()

            # everything else  
            else:
                l2[i][j] = ((l2[i-1][j] + l2[i][j-1])/2 + getVar())

    #l3
    for j in range(SIZE):
        if j==0:
            if not l3 in PLANES:
                break
            y+=1
            print("\nPopulating discrete plane("+str(y)+"/"+str(len(PLANES))+")",end="...")
            x=0
        for i in range(SIZE):

            # progress bar
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")
            x+=1
            
            # top left
            if i == 0 and j == 0:
                l3[i][j] = getVal()

            #edges

            # top row
            elif i > 0 and j == 0:
                l3[i][j] = l3[i][j-1] + getVar()
            else:
                #print(l[i-1][j-1], l[i-1][j], l[i-1][j+1])
                if i < SIZE-1: 
                    #l[i][j] = (l[i-1][j-1] + l[i-1][j] + l[i-1][j+1] + l[i][j-1])/4 + getVar()
                    l3[i][j] = (l3[i-1][j-1] + l3[i][j-1] + l3[i+1][j-1])/3 + getVar()

                elif i == SIZE-1: # wrap around on right edge (0 does it for us with -1)
                    l3[i][j] = (l3[i-1][j-1] + l3[i][j-1] + l3[0][j-1])/3 + getVar()

    #l4
    for i in range(SIZE):
        if i==0:
            if not l4 in PLANES:
                break
            y+=1
            print("\nPopulating discrete plane("+str(y)+"/"+str(len(PLANES))+")",end="...")
            x=0

        for j in range(SIZE-1,-1,-1):
            # progress bar
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")
            x+=1

            # top corner
            if i == 0 and j == SIZE-1:
                l4[i][j] = getVal()

            #edges
            elif i == 0 and j < SIZE-1:
                l4[i][j] = l4[i][j+1] + getVar()
            elif i > 0 and j == SIZE-1:
                l4[i][j] = l4[i-1][j] + getVar()

            # everything else  
            else:
                l4[i][j] = ((l4[i-1][j] + l4[i][j+1])/2 + getVar())

    for i in range(SIZE):
        if i==0:
            if len(PLANES)==1:
                l=PLANES[0]
                break
            print("\nCombining planes",end="...")
            x=0

        for j in range(SIZE):
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")
            x+=1
            if l1:
                l[i][j] += l1[i][j]
            if l2:
                l[i][j] += l2[i][j]
            if l3:
                l[i][j] += l3[i][j]
            if l4:
                l[i][j] += l4[i][j]
            l[i][j] /= len(PLANES)
    print("Done.")
    
    """
    print("Adding features",end="...")
    features=[[random.randint(0,SIZE),random.randint(0,SIZE)] for i in range(5)]

    x=0 # progress

    for i in range(SIZE):
        for j in range(SIZE):
            # progress bar
            if (x%(SIZE*SIZE/10) == 0):
                print(str(int(x/(SIZE*SIZE)*100))+"%",end="...")

            x += 1
                
            for f in features:
                size = 500
                
                distance=((i-f[0])**2+(j-f[1])**2)**.5

                if distance==0 or distance > size:
                    continue
                
                num = (size-distance)/size# 0-1
                m=10 # peak height
                
                if f[0]%2==0:
                    l[i][j]+=m*num
                else:
                    l[i][j]-=m*num

    """
    
    # stats
    minimum = GLOBALMIN[2] = sorted(sorted(l, key=lambda y:min(y))[0])[0]
    maximum = sorted(sorted(l, key=lambda y:max(y))[-1])[-1]
    for line, row in enumerate(l):
        if minimum in row:
            GLOBALMIN[0]=line
            GLOBALMIN[1]=row.index(minimum)
            break                

    print("Done.")

# Populates window with data points, returns win object
def makeWin():
    global SIZE, WINSIZE, l, SEARCH, GLOBALMIN, BEST, RESOLUTION, \
    crawler_hist, minimum, maximum

    win = GraphWin("Search-Visualizer",WINSIZE,WINSIZE)

    #### COLORS
    #http://www.science.smith.edu/dftwiki/images/thumb/3/3d/TkInterColorCharts.png/700px-TkInterColorCharts.png
    COLORS_BLUEISH=[
            "Yellow",
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
    
    COLORS_BW=["White","Black"]

    COLORS_MORDOR=["#000000",
                 "#FF0000",
                 "#555555",
                 "#990033",
                 "#FFCC00",
                 "#FFFF66"]

    COLORS_NEBULA=["#FFFFFF",
                   "#000000",
                   "#FF00FF"]

    
    COLORS=COLORS_BLUEISH
    GRADIENT=True

    # Get color codes in dec
    c_CONV=65535/255
    COLORS=list(map(lambda x: [win.winfo_rgb(x)[0]//c_CONV,
                               win.winfo_rgb(x)[1]//c_CONV,
                               win.winfo_rgb(x)[2]//c_CONV],
                    COLORS))
    
    #####

    ## ANIMATIONS
    # lambdas that sort in place
    ANIMATIONS={"VALUE" : lambda g: g.sort(key=lambda x: l[x[0]][x[1]]),
                "VALUE_REV" : lambda g: g.sort(key=lambda x: l[x[0]][x[1]],
                       reverse=True),
                "RANDOM" : lambda g: g.sort(key=lambda x: random.uniform(0,1)),
                "SWIPE" : lambda g: g.sort(key=lambda x: x[0]+x[1]),
                "SWIPE_REV" : lambda g: g.sort(key=lambda x: x[0]+x[1],
                       reverse=True),
                "CROSS" : lambda g: g.sort(key=lambda x:  \
                                           x[random.choice([0,1])]),
                "CROSS_REV" : lambda g: g.sort(key=lambda x:  \
                                               x[random.choice([0,1])],reverse=True),
                "CURTIAN" : lambda g: g.sort(key=lambda x: x[1]),
                "CURTIAN_REV" : lambda g: g.sort(key=lambda x: x[1], reverse=True),
                "REVEAL" : lambda g: g.sort(key=lambda x:  \
                                            abs(x[0]-(SIZE//2)+x[1]-(SIZE//2))),
                "REVEAL_REV" : lambda g: g.sort(key=lambda x:  \
                                            abs(x[0]-SIZE//2+x[1]-SIZE//2),
                                          reverse=True),
                "RADIAL" : lambda g: g.sort(key=lambda x:  \
                                            ((x[0]-SIZE//2)**2+(x[1]-SIZE//2)**2)**1/2),
                "RADIAL_REV" : lambda g: g.sort(key=lambda x: \
                                            ((x[0]-SIZE//2)**2+(x[1]-SIZE//2)**2)**1/2,
                                          reverse=True),
                "REV" : lambda g: g.sort(key=lambda x:x, reverse=True),
                "DEFAULT" : lambda g: g.sort(key=lambda x:x)}
########################## A N I M A T I O N    P R E S E T S ###############################
######### Zig Zag
#    PRESORT=True # sort the points before breaking them up
#    PRESORT_TYPE="CURTIAN"
#    CHUNKS=100
#    SHUFFLE_CHUNKS=False
#    anim_list=["SWIPE","SWIPE_REV"]*(CHUNKS//2+1)
######### Patchwork
#    PRESORT=True # sort the points before breaking them up
#    PRESORT_TYPE="CROSS"
#    CHUNKS=20
#    SHUFFLE_CHUNKS=True
#    anim_list=["SWIPE","SWIPE_REV"]*(CHUNKS//2+1)
######### Bars!
#    PRESORT=True # sort the points before breaking them up
#    PRESORT_TYPE="REVEAL"
#    CHUNKS=10
#    SHUFFLE_CHUNKS=True
#    anim_list=["DEFAULT","REV"]*(CHUNKS//2+1)
######### Spotlight
#    PRESORT=True # sort the points before breaking them up
#    PRESORT_TYPE="RANDOM"
#    CHUNKS=19
#    SHUFFLE_CHUNKS=False
#    anim_list=["RADIAL_REV","RADIAL"]*(CHUNKS//2+1)
######### Funky Circles
#    PRESORT=True # sort the points before breaking them up
#    PRESORT_TYPE="RADIAL_REV"
#    CHUNKS=10
#    SHUFFLE_CHUNKS=False
#    anim_list=["RADIAL"]*(CHUNKS-1)+["RANDOM"]
######### Scanner
#    PRESORT=True # sort the points before breaking them up
#    PRESORT_TYPE="VALUE"
#    CHUNKS=20
#    SHUFFLE_CHUNKS=False
#    anim_list=["CROSS","CROSS_REV"]*(CHUNKS//2+1)
######### ENHANCE!
    PRESORT=True # sort the points before breaking them up
    PRESORT_TYPE="VALUE_REV"
    CHUNKS=20
    SHUFFLE_CHUNKS=False
    anim_list=["RADIAL"]*CHUNKS
######### Classic
#    PRESORT=False # sort the points before breaking them up
#    PRESORT_TYPE="DEFAULT"
#    CHUNKS=1
#    SHUFFLE_CHUNKS=False
#    anim_list=["VALUE"]
######### RANDOM
#    PRESORT=True # sort the points before breaking them up
#    PRESORT_TYPE=random.choice(list(ANIMATIONS.keys()))
#    CHUNKS=random.randint(1,100)
#    SHUFFLE_CHUNKS=True
#    anim_list=[random.choice(list(ANIMATIONS.keys())) for i in range(CHUNKS)]

    print("Prepping points",end="...")

    # sort points
    points=[]
    chunks=[]

    # get initial list
    for i in range(SIZE):
        for j in range(SIZE):
            points.append([i,j])
    if PRESORT:
        ANIMATIONS[PRESORT_TYPE](points)

    # divide into chunks and set order
    for i in range(CHUNKS):
        chunks.append(points[i*len(points)//CHUNKS:(i+1)*len(points)//CHUNKS])

    if SHUFFLE_CHUNKS:
        random.shuffle(chunks)
        
    for chunk in chunks:
        ANIMATIONS[anim_list.pop(0)](chunk)

    points=[]
    for chunk in chunks:
        points += chunk
        
    print("\nDrawing discrete plane",end="...")
    x=0
    
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
                    sample=max(sample,1) # or divide by 0
                    
                    for q in range(sample):
                        for w in range(sample):
                            cellVal += l[i+q][j+w]

                    cellVal /= sample**2
                    
                # 0 to 1 (doesn't touch 1)
                num=(cellVal-minimum)/(maximum-minimum+1)

                # num=str(int((l[i][j]-minimum)/((maximum-minimum))*100))[:1]
                
                if not GRADIENT:
                    num *=len(COLORS)
                    color="#{0:02x}{1:02x}{2:02x}".format(int(COLORS[int(num)][0]),
                                                          int(COLORS[int(num)][1]),
                                                          int(COLORS[int(num)][2]))
                    
                elif GRADIENT:

                    num *= (len(COLORS)-1)
                    
                    color1=COLORS[int(num)]
                    try:
                        color2=COLORS[int(num)+1]
                    except IndexError: # in case somehow num = 1
                        print(num)
                        print(maximum,minimum,cellVal)

                    # components
                    r1=color1[0]
                    r2=color2[0]
                    g1=color1[1]
                    g2=color2[1]
                    b1=color1[2]
                    b2=color2[2]
                    
                    # get ratio
                    ratio=num-int(num)
                    rN = int((1-ratio)*r1 + (ratio)*r2) 
                    gN = int((1-ratio)*g1 + (ratio)*g2)
                    bN = int((1-ratio)*b1 + (ratio)*b2)

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
    #   FINAL CRAWLER LOC
    #   GLOBAL BEST
    #   BEST FOUND
    COLORS_WHITE=["white",
                  "lemon chiffon",
                  "papaya whip",
                  "old lace",
                  "red",
                  "blue",
                  "magenta"]    
    COLORS_BRIGHT=["white",
                   "yellow",
                   "magenta",
                   "red",
                   "black",
                   "grey",
                   "pink"]
                   
    CRAWLER_COLORS=COLORS_BRIGHT

    # P H A S E 1
    print("PHASE1")
    phase1=[]

    # DISTRIBUTE X CRAWLERS WITH Y GREED FOR Z STEPS
    X=500
    Y=100
    Z=1
    
    for i in range(X):
        c = Crawler(Y, random.randint(0,SIZE-1), random.randint(0,SIZE-1))
        phase1.append(c)

    for i in range(Z):
        for c in phase1:
            c.update()
            if i%2==0:
                win.plot(c.x,c.y,CRAWLER_COLORS[0])

    # P H A S E 2
    print("PHASE2") 
    phase2=[]

    # PICK TOP X CRAWLERS, DISTRIBUTE Y CRAWLERS WITH Z GREED AT THEIR LOCATIONS RUNNING Q TIMES
    X=4
    Y=2
    Z=4
    Q=500

    phase1 = sorted(phase1, key=lambda x: x.value)[:X]

    for i in phase1:
        for j in range(Y):
            c = Crawler(Z, i.x, i.y)
            phase2.append(c)

    for i in range(Q):
        for c in phase2:
            c.update()
            if i%2==0:
                win.plot(c.x,c.y,CRAWLER_COLORS[1])

    # P H A S E 3
    print("PHASE3")
    phase3=[]

    # PICK TOP X CRAWLERS, DISTRIBUTE Y CRAWLERS WITH Z GREED AT THEIR LOCATIONS RUNNING Q TIMES
    X=2
    Y=1
    Z=10
    Q=500

    phase2 = sorted(phase2, key=lambda x: x.value)[:X]

    for i in phase2:
        for j in range(Y):
            c = Crawler(Z, i.x, i.y)
            phase3.append(c)
            
    for i in range(Q):
        for c in phase3:
            c.update()
            if i%2==0:
                win.plot(c.x,c.y,CRAWLER_COLORS[2])

    print("FINAL PHASE")

    # HILL CLIMBER WITH TOP CLIMBER
    climber = min(phase3, key=lambda x: x.value)
    climber.greed = 1000

    for i in range(100):
        climber.update()
        if i%2==0:
            win.plot(climber.x,climber.y,CRAWLER_COLORS[3])

    print("DONE")

    # Stats
    print("Best Solution Found:",BEST[2],"\nGlobal Minimum:",GLOBALMIN[2])
    if BEST[2] == GLOBALMIN[2]:
        print("GLOBAL MIN FOUND")
    #crawler_hist[climber.x][climber.y] = -1 # mark finish spot

    finish = Circle(Point(climber.x,climber.y),5)
    globalmin = Circle(Point(GLOBALMIN[0],GLOBALMIN[1]),4)
    best = Circle(Point(BEST[0],BEST[1]),3)

    finish.setFill(CRAWLER_COLORS[4])
    globalmin.setFill(CRAWLER_COLORS[5])
    best.setFill(CRAWLER_COLORS[6])
    finish.setOutline(CRAWLER_COLORS[4])
    globalmin.setOutline(CRAWLER_COLORS[5])
    best.setOutline(CRAWLER_COLORS[6])
    
    finish.draw(win)
    globalmin.draw(win)
    best.draw(win)


    print(CRAWLER_COLORS[4].upper(), "DOT: Final crawler endpoint")
    print(CRAWLER_COLORS[5].upper(), "DOT: Global minimum")
    print(CRAWLER_COLORS[6].upper(), "DOT: Best solution found")

    #for i in range(len(crawler_hist)):
    #    for j in range(len(crawler_hist[i])):
    #        if crawler_hist[i][j] > 3:
    #            win.plot(i,j,"red")
    #        elif crawler_hist[i][j] > 0:
    #            win.plot(i,j,"red3")

    print(SEARCH,"points searched,",str(round((SEARCH/(SIZE*SIZE))*100,3))+"% of points.")
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
    print("Done.")
    file.close()

def main():
    makeData()
    fireworkSearch(makeWin())
    input("====INPUT NEWLINE TO EXIT====")

if (__name__) == "__main__":
    main()
