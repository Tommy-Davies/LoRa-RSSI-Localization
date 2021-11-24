import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

#overlay a picture over the plot
# im = plt.imread("map1.png")
#implot = plt.imshow(im)

def animate(xar, yar):
    #creating x and y arrays
    # xar = []
    # yar = []

    #populating thr arrays with get_data func
    # get_data(xar,yar)
    #clearing previous line
    ax1.clear()
    #drawing line again wiht new data
    ax1.scatter(xar,yar)
    #making the overlay visible
    # implot = plt.imshow(im)

def get_data(xar,yar):
    #figure out what pins the data is going to be coming form. Going to write to a file with [x,y] format, then update the xar array
    pullData = open("sampleText.txt", "r").read()
    dataArray = pullData.split('\n')

    for eachLine in dataArray:
        if len(eachLine) > 1:
            x, y = eachLine.split(',')
            xar.append(int(x))
            yar.append(int(y))
            # plt.scatter([10], [20])