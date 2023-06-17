import laspy 
import numpy as np
import matplotlib.pyplot as plt

def laz2png(file, x0, y0, dx, dy):
    "creates png from laser scan data"
    las = laspy.read(file)
    las.points = las.points[las.classification == 2]    # 2: 0 m, 3: <0,5, 4: 0,5-2, 5: 2-50
    xmin = min(las.points.x)
    las.points = las.points[las.x >= xmin+x0]
    las.points = las.points[las.x <= xmin+x0+dx]
    ymin = min(las.points.y)
    las.points = las.points[las.y >= ymin+y0]
    las.points = las.points[las.y <= ymin+y0+dy]
    zmin = min(las.points.z)
    x = np.array(las.points.x)
    y = np.array(las.points.y)
    z = np.array(las.points.z)
    x -= (xmin+x0)
    x = x.astype(int)
    y -= (ymin+y0)
    y = y.astype(int)
    z -= zmin
    z = z.astype(int)
    a = np.stack((x,y,z), axis=1)
    dsm = np.zeros((dy+1, dx+1))
    for i in a:
        if i[2] != 0:
            dsm[i[1], i[0]] = i[2]
    dsm = dsm[::-1]
    plt.imsave(f"{file[:-4]}_part_.png", dsm, cmap="gray")
    plt.show()

def show_png(img):
    dsm = plt.imread(img)
    plt.imshow(dsm, cmap="gray")
    plt.colorbar()
    plt.show()

def fill_fw(img, dy, dx):
  "fills the previous zero dot"
    dsm = plt.imread(img)
    r = 0
    for row in dsm:
        c = 0
        for i in row:
            try:
                if i[0] == 0 and dsm[r+dy, c+dx][0] != 0:
                    dsm[r,c] = dsm[r+dy, c+dx]
            except:
                pass
            c += 1
        r += 1
    plt.imsave(f"{file[:-4]}_part_wf.png", dsm, cmap="gray")

def fill_bw(img, dy, dx):
  "fills zero in the next pixel"
    dsm = plt.imread(img)
    r = 0
    for row in dsm:
        c = 0
        for i in row:
            try:
                if i[0] == 0 and dsm[r+dy, c+dx][0] != 0 and dsm[r-dy, c-dx][0] != 0:
                    dsm[r,c] = dsm[r+dy, c+dx]
            except:
                pass
            c += 1
        r += 1
    plt.imsave(f"{file[:-4]}_part_wf.png", dsm, cmap="gray")

if __name__=="__main__":
    file = "N4332D2.laz"    # Maanmittauslaitoksen laserkeilausaineisto, keilattu 2022-06-23, 3x3 km alue 
    x0 = 000   #0-3000
    dx = 3000    #leveys <= 3000 - x0
    y0 = 000    #0-3000
    dy = 3000    #korkeus <= 3000 - y0
    # laz file to raw png file
    laz2png(file, x0, y0, dx, dy)
    # filling zeros, [right, below, left, above] * 3 -> shore lines < 2 m offshore
    fill_fw(f"{file[:-4]}_part_.png", 0, 1)     # saved to another file to keep the original
    fill_fw(f"{file[:-4]}_part_wf.png", 1, 0)
    fill_bw(f"{file[:-4]}_part_wf.png", 0, -1)
    fill_bw(f"{file[:-4]}_part_wf.png", -1, 0)
    fill_fw(f"{file[:-4]}_part_wf.png", 0, 1)
    fill_fw(f"{file[:-4]}_part_wf.png", 1, 0)
    fill_bw(f"{file[:-4]}_part_wf.png", 0, -1)
    fill_bw(f"{file[:-4]}_part_wf.png", -1, 0)
    fill_fw(f"{file[:-4]}_part_wf.png", 0, 1)
    fill_fw(f"{file[:-4]}_part_wf.png", 1, 0)
    fill_bw(f"{file[:-4]}_part_wf.png", 0, -1)
    fill_bw(f"{file[:-4]}_part_wf.png", -1, 0)
    #show_png(f"{file[:-4]}_part_wf.png")
