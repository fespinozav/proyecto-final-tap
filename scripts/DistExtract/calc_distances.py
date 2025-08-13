import numpy as np
import os
import sys
import math

# Output: Numpy array with 
#         # X = Query name
#         # Y = Target name
#         # iXY := sum of identical base pairs over all HSPs
#         # hXY = total length of all HSPs
#         # lamXY = sum of both genomes’ lengths
#         # minXY = twice the length of the smallest genome
# print(f"{query_name-v-target_name},{iXY},{hXY},{lamXY},{minXY}")


dir=sys.argv[1]
# sel=sys.argv[2].split(",")


def unite_npy(dir):
    if "labels.npy" in os.listdir(dir) and "hsps.npy" in os.listdir(dir):
        labels=np.load(os.path.join(dir,'labels.npy'))
        hsp=np.load(os.path.join(dir,'hsps.npy'))
        return labels,hsp
    else:
        tmp_labels=[]
        tmp_hsps=[]
        for file in os.listdir(dir):
            if file.startswith("hsps_"):
                tmp_hsps.extend(np.load(os.path.join(dir,file)))
                tmp_labels.extend(np.load(os.path.join(dir,file.replace("hsps_","labels_"))))
        np.save(os.path.join(dir,'labels.npy'),tmp_labels)
        np.save(os.path.join(dir,'hsps.npy'),tmp_hsps)
        return np.array(tmp_labels),np.array(tmp_hsps)


# Unify all np files
labels,hsp=unite_npy(dir)

print(labels.shape)




# TEST
# ---
# print(labels)
# print(labels.shape)
# print(np.where(labels == "NZ_AP017581-v-NZ_AP017578"))
# print(labels[np.where(labels == "NZ_AP017581-v-NZ_AP017578")[0].item()])
# ---

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





def calc_distance_back(labels,hsp):
    temp_d0=[]
    temp_d1=[]
    for item, value in zip(labels,hsp):
        isplit=item.item().split("-v-")
        label=f"{isplit[1]}-v-{isplit[0]}"

        xy=value
        # Get corresponding reverse alignment (YX)
        # if np.where(labels == label)[0].size != 0:
        #     pos=np.where(labels == label)[0].item()
        #     # print(f"{pos} {item.item()}")
        #     yx=hsp[pos]
        # else:
        #     print(f"No {item.item()} found")

        yx=get_reverse(labels,label,hsp)


        temp_d0.append(dis0(xy[1],yx[1],xy[2]))
        temp_d1.append(dis1(xy[1],yx[1],xy[3]))



    d0=np.array(temp_d0)
    d1=np.array(temp_d1)

    return d0, d1


def get_reverse(labels,label,hsp):
            # Get corresponding reverse alignment (YX)
            if np.where(labels == label)[0].size != 0:
                pos=np.where(labels == label)[0].item()
                # print(f"{pos} {item.item()}")
                
                return hsp[pos]
            else:
                print(f"No {label} found")
                return [0,0,0,0]
            

def calc_distance(labels,hsp,sel):
    # temps_dict={
    # "d0":temp0=[],
    # "d1":temp1=[],
    # "d2":temp2=[],
    # "d3":temp3=[],
    # "d4":temp4=[],
    # "d5":temp5=[],
    # "d6":temp6=[],
    # "d7":temp7=[],
    # "d8":temp8=[],
    # "d9":temp9=[]
    # }

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

    


        


sel=sys.argv[2].split(",")
sel=[int(x) for x in sel]



results=calc_distance(labels,hsp,sel)

for arr,ele in zip(results,sel):
    np.save(f"distances_d{ele}.npy",arr)






