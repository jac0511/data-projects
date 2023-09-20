import laspy
from numpy import array, empty, nan, dstack, isnan, reshape, concatenate, copy
from pandas import DataFrame
from matplotlib.pyplot import imsave, imread
from datetime import datetime

z_min = 1000
z_max = 0

def laz2df(file:str, x0:int, y0:int, dx:int, dy:int, layer:int):
    "creates .png from laser scan data (.laz)"
    las = laspy.read(file)
    #las.points = las.points[las.classification == 2]    # 2: 0 m, 3: <0,5, 4: 0,5-2, 5: 2-50
    df = DataFrame({"x":array(las.x), "y":array(las.y), "z":array(las.z), "classification":array(las.classification)}).astype(int)
    df.x = df.x - df.x.min()
    df.y = df.y - df.y.min()
    if layer == 2:
        global z_min
        if z_min > df.z.min():
            z_min = df.z.min()
        global z_max
        if z_max < df.z.max():
            z_max = df.z.max()
    elif layer == 5 and layer not in df.classification.value_counts().index:
        #print(layer)
        layer = 3
    #df.z = df.z - (z_min - 5)
    df = df[df.x >= x0][df.x < x0+dx][df.y >= y0][df.y < y0+dy][df.classification == layer].reset_index(drop=True)
    #print(df.describe())
    dsm = empty((dx, dy))
    dsm.fill(nan)
    #print("data  ", datetime.now())
    dsm[df.y, df.x] = df.z
    #if layer ==2:
    #else:
    dsm = DataFrame(dsm, range(dx), range(dy))
    #print("table ", datetime.now())
    return dsm

def fill_gaps(dsm):
    for i in range(5):
        dsm = enlarge_dots(dsm)
    return dsm

def enlarge_dots(dsm):
    dsm = dsm.ffill(axis=0, limit=1).bfill(axis=0, limit=1)
    dsm = dsm.ffill(axis=1, limit=1).bfill(axis=1, limit=1)
    return dsm

def save_img(img, nimi:str, cmap:str, hmin, hmax):
    img = img.fillna(0).astype(int)
    img = img.iloc[::-1]
    imsave(f"{nimi}.png", img, cmap=cmap, vmin=hmin, vmax=hmax)

def colourful_vege(vege, nimi:str):
    bushes = vege[vege <= 4]
    bushes = enlarge_dots(bushes)
    bushes = ((bushes + 1) / 6).fillna(0).iloc[::-1]
    middle = vege[vege <= 14]
    middle = middle[middle > 4]
    middle = enlarge_dots(middle)
    middle = (1 - ((middle - 4) / 11)).fillna(0).iloc[::-1]
    forest = vege[vege > 14]
    forest = forest[forest <= 70]
    forest = enlarge_dots(forest)
    forest = ((forest - 13) / 57).fillna(0).iloc[::-1]
    print(bushes.max().max(), middle.max().max(), forest.max().max())
    print(bushes.min().min(), middle.min().min(), forest.min().min())
    imsave(f"{nimi}.png", dstack((bushes, forest, middle)))

def liitos(lista, rows, cols, nimi, malli):
    i = 0
    #print(lista)
    arr = list(copy(lista))
    #print(arr)
    for n in arr:
        #print(""+malli+"_"+n[:-3]+"png")
        arr[i] = ""+malli+"_"+n[:-3]+"png"
        i += 1
    arr = reshape(arr, (rows, cols))
    #print(arr)
    kuvar = []
    for row in arr:
        kuvac = []
        for col in row:
            kuva = imread(col, format="png")
            if kuvac == []:
                kuvac = kuva
            else:
                kuvac = concatenate((kuvac, kuva), axis=1)
        if kuvar == []:
            kuvar = kuvac
        else:
            kuvar = concatenate((kuvar, kuvac), axis=0)
    imsave(f"{nimi}_{malli}_{arr[0,0][-7:-4]}.png", kuvar)
    #print(lista)

if __name__=="__main__":
    # Maanmittauslaitoksen laserkeilausaineisto, keilattu 2012 ja 2022-06-23, 3x3 km alue 
    toivakka = ["N4341A3_12.laz", "N4341C1_12.laz", "N4341C3_12.laz", "N4332B4_22.laz", "N4332D2_22.laz", "N4332D4_22.laz", "N4332B3_22.laz", "N4332D1_22.laz", "N4332D3_22.laz"] 
    #kkm = ["kasvusto", "korkeus", "metsa"]
    #for malli in kkm:
    #    liitos(toivakka, 3,3, "toivakka", malli)
    #quit()
    print("start  ", datetime.now())
    for file in toivakka:                                        #   nimi
        x0 = 000    #0-3000
        dx = 3000    #leveys <= 3000 - x0
        y0 = 000    #0-3000
        dy = 3000    #korkeus <= 3000 - y0
        hmin = 100                                              #   korot
        hmax = 200
        print(file)
        #print("start  ", datetime.now())
        raw_img = laz2df(file, x0, y0, dx, dy, 2)
        filled = fill_gaps(raw_img)
        save_img(filled, f"korkeus_{file[:-4]}", "gist_earth", hmin, hmax)
        #print("korkeus", datetime.now())
        vege = laz2df(file, x0, y0, dx, dy, 5)
        vege -= filled
        if int(file[-6:-4]) < 22:
            print(int(file[-6:-4]))
            k= 90/(vege+15)*0.07
            vk = 22 - int(file[-6:-4])
            vege += k*vk
        vege = vege[vege >= -1]
        save_img(vege, f"kasvusto_{file[:-4]}", "gray", 0, 60)
        #print("kasvit ", datetime.now())
        colours = colourful_vege(vege, f"metsa_{file[:-4]}")
    kkm = ["kasvusto", "korkeus", "metsa"]
    for malli in kkm:
        liitos(toivakka, 3,3, "toivakka", malli)                  #   nimi, koko
    print("finish ", datetime.now(), "- h =", z_min, "-", z_max)
    
