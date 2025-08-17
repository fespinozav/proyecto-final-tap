import numpy as np
import sys
import math
import multiprocessing
import time


# X = Query name
# Y = Target name
# iXY := sum of identical base pairs over all HSPs
# hXY = total length of all HSPs
# lamXY = sum of both genomes’ lengths
# minXY = twice the length of the smallest genome


files=sys.argv[1].split(" ")
sel=sys.argv[2].split(",")
sel=[int(x) for x in sel]


def unite_npy(files):
            
        tmp_labels=[]
        tmp_hsps=[]
        for file in files:
            if file.startswith("hsps_"):
                tmp_hsps.extend(np.load(file))
                tmp_labels.extend(np.load(file.replace("hsps_","labels_")))
        return np.array(tmp_labels),np.array(tmp_hsps)


# Unify all npy files
labels,hsp=unite_npy(files)


# Formulae
# ------------------------------------------------------------
# Group A

def dis0(hXY,hYX,lamXY):
    # d0 = 1-(hXY+hYX)/(lamXY)
    return 1-((int(hXY)+int(hYX))/int(lamXY))
def dis1(hXY,hYX,minXY):
    # d1 = 1-(hXY+hYX)/(minXY)
    return 1-((int(hXY)+int(hYX))/int(minXY))
def dis2(hXY,hYX,lamXY):
    # d2 = -log((hXY+hYX)/(lamXY))
    return -math.log(((int(hXY)+int(hYX))/int(lamXY)),10)
def dis3(hXY,hYX,minXY):
    # d3 = -log((hXY+hYX)/(minXY))
    return -math.log(((int(hXY)+int(hYX))/int(minXY)),10)

# Group B

def dis4(hXY,hYX,iXY):
    return 1-((2*int(iXY))/(int(hXY)+int(hYX)))
def dis5(hXY,hYX,iXY):
    return -math.log(((2*int(iXY))/(int(hXY)+int(hYX))),10)

# Group C

def dis6(iXY,lamXY):
    return 1-((2*int(iXY))/int(lamXY))
def dis7(iXY,minXY):
    return 1-((2*int(iXY))/int(minXY))
def dis8(iXY,lamXY):
    return -math.log(((2*int(iXY))/(int(lamXY))))
def dis9(iXY,minXY):
    return -math.log(((2*int(iXY))/(int(minXY))))
# -----------------------------------------------------------


# Inputs
# [0]    [1]    [2]     [3]
# [iXY] [hXY] [lamXY] [minXY]

def get_reverse(labels,label,hsp):
            # Get corresponding reverse alignment (YX)
            if np.where(labels == label)[0].size != 0:
                pos=np.where(labels == label)[0].item()
                
                return hsp[pos]
            else:
                return [0,0,0,0]
            

def calc_distance_vector(labels,hsp,sel):
    dis_list=[dis0,dis1,dis2,dis3,dis4,dis5,dis6,dis7,dis8,dis9]

    temps={
    0:[],
    1:[],
    2:[],
    3:[],
    4:[],
    5:[],
    6:[],
    7:[],
    8:[],
    9:[]
    }

    for item, value in zip(labels,hsp):
        isplit=item.item().split("-v-")
        label=f"{isplit[1]}-v-{isplit[0]}"
        
        xy=value
        yx=get_reverse(labels,label,hsp)


        # [0]    [1]    [2]     [3]
        # [iXY] [hXY] [lamXY] [minXY]

        # Require reverse dis 
        # input1=[xy[1],yx[1],xy[2]] # 0 y 2
        # input2=[xy[1],yx[1],xy[3]] # 1 y 3
        # input3 =[xy[1],yx[1],xy[0]] # 4 y 5

        # # No reverse
        # input4=[xy[0],xy[2]] # 6 y 8
        # input5=[xy[0],xy[3]] # 7 y 9


        if 0 in sel:
            temps[0].append(dis_list[0](xy[1],yx[1],xy[2]))
        if 2 in sel:
            temps[2].append(dis_list[2](xy[1],yx[1],xy[2]))
        
        if 1 in sel:
            temps[1].append(dis_list[1](xy[1],yx[1],xy[3]))
        if 3 in sel:
            temps[3].append(dis_list[3](xy[1],yx[1],xy[3]))
        
        if 4 in sel:
            temps[4].append(dis_list[4](xy[1],yx[1],xy[0]))
        if 5 in sel:
            temps[5].append(dis_list[5](xy[1],yx[1],xy[0]))

        
        if 6 in sel:
            temps[6].append(dis_list[6](xy[0],xy[2]))
        if 8 in sel:
            temps[8].append(dis_list[8](xy[0],xy[2]))


        if 7 in sel:
            temps[7].append(dis_list[7](xy[0],xy[3]))
        if 9 in sel:
            temps[9].append(dis_list[9](xy[0],xy[3]))
        
    re_list=[]
    for ele in sel:
        re_list.append(np.array(temps[ele]))

    return re_list 

      
# Distances vector
# results=calc_distance_vector(labels,hsp,sel)
# for arr,ele in zip(results,sel):
#     np.save(f"distances_d{ele}.npy",arr)

# Distances matrix


new_labels=[]
for i in labels:
    new_labels.append(i.item().split("-v-")[0])

uni_labels=np.unique(np.array(new_labels))
ll=len(uni_labels)


def get_rows(name):
    row=[]
    for j in range(ll):
        label=f"{name}-v-{uni_labels[j]}"
        if np.where(labels == label)[0].size != 0:
            pos=np.where(labels == label)[0].item()
            row.append(dis_by_name(hsp[pos],label))
        else:
            row.append(dis_by_name([1,1,1,1],label))
    print("done")
    return {name:row}

def dis_by_name(xy,label):
    dis_list=[dis0,dis1,dis2,dis3,dis4,dis5,dis6,dis7,dis8,dis9]
    temps={
    0:[],
    1:[],
    2:[],
    3:[],
    4:[],
    5:[],
    6:[],
    7:[],
    8:[],
    9:[]
    }

    yx=get_reverse(labels,label,hsp)


    # [0]    [1]    [2]     [3]
    # [iXY] [hXY] [lamXY] [minXY]

    # Require reverse dis 
    # input1=[xy[1],yx[1],xy[2]] # 0 y 2
    # input2=[xy[1],yx[1],xy[3]] # 1 y 3
    # input3 =[xy[1],yx[1],xy[0]] # 4 y 5

    # # No reverse
    # input4=[xy[0],xy[2]] # 6 y 8
    # input5=[xy[0],xy[3]] # 7 y 9


    if 0 in sel:
        temps[0].append(dis_list[0](xy[1],yx[1],xy[2]))
    if 2 in sel:
        temps[2].append(dis_list[2](xy[1],yx[1],xy[2]))
    
    if 1 in sel:
        temps[1].append(dis_list[1](xy[1],yx[1],xy[3]))
    if 3 in sel:
        temps[3].append(dis_list[3](xy[1],yx[1],xy[3]))
    
    if 4 in sel:
        temps[4].append(dis_list[4](xy[1],yx[1],xy[0]))
    if 5 in sel:
        temps[5].append(dis_list[5](xy[1],yx[1],xy[0]))

    
    if 6 in sel:
        temps[6].append(dis_list[6](xy[0],xy[2]))
    if 8 in sel:
        temps[8].append(dis_list[8](xy[0],xy[2]))


    if 7 in sel:
        temps[7].append(dis_list[7](xy[0],xy[3]))
    if 9 in sel:
        temps[9].append(dis_list[9](xy[0],xy[3]))
    
    re_list=[]
    for ele in sel:
        re_list.extend(np.array(temps[ele]))

    return re_list 




def calc_distance_matrix(inputs):
    pool = multiprocessing.Pool()
    pool = multiprocessing.Pool(processes=len(uni_labels))
    # inputs = ['NZ_CP018914','NZ_CP018913','NC_010263','NZ_CP015015']
    outputs = pool.map(get_rows, inputs)

    z={}
    for x in outputs:
        z=z|x

    new_array=[]
    for i in inputs:
        new_array.append(z[i])
    return new_array


start=time.perf_counter()

dist_matrix=calc_distance_matrix(uni_labels)
np.save("distances_matrix.npy",dist_matrix)
np.save("unique_labels.npy",uni_labels)

end=time.perf_counter()
print(f"Time: {end-start}")

