#!/usr/bin/python3.2
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@ethz.ch>
# Date:    11.04.2014 13:08:23 CEST
# File:    read_mmn.py

import numpy as np
#~ def check(A):
    #~ x = np.array(A)
    #~ B = x - x.transpose()
    #~ print(B)
    #~ for temp in B:
        #~ for temp2 in temp:
            #~ if(abs(temp2)>1e-9):
                #~ return False
    #~ return True
    
def getM(mmn_file):
    f = open(mmn_file, "r")
    f.readline()
    
    # read the first line
    line = list(filter(None,f.readline().split(" ")))
    num_bands, num_kpts, nntot = [int(l) for l in line]
    
    # read the rest of the file
    data = f.read()
    f.close()
    
    
    data = list(filter(None,data.split("\n")))
    blocks = []
    step = num_bands * num_bands + 1
    for i in range(0, len(data) , step):
        blocks.append(list(filter(None,data[i:i + step])))
    
    # extract k and k + b for each M
    idx_list = []
    for i in range(len(blocks)):
        idx_list.append([int(el) for el in list(filter(None, blocks[i][0].split(" ")))[:2]])
    
    # extract M
    M = []
    for i in range(len(blocks)):
        # check if element has to be in the string
        if(idx_list[i][0] % num_kpts - idx_list[i][1] != -1):
            continue
        # end check
        temp = []
        for j in range(1, len(blocks[i])):
            temp2 = [float(k) for k in list(filter(None, blocks[i][j].split(" ")))]
            temp.append(temp2[0] + 1j * temp2[1])
        
        temp2 = []
        for j in range(0, len(temp), num_bands):
            temp2.append(temp[j:j + num_bands])
            #~ temp2.append([x / num_bands for x in temp[j:j + num_bands]] )  # DEBUG
        
        import numpy as np # DEBUG
        #~ M.append(np.array([list(x) for x in zip(*temp2)]).transpose())
        #~ print(check([list(x) for x in zip(*temp2)]))
        M.append([list(x) for x in zip(*temp2)])
        
    
    
    return M
    


#~ M = getM("test/wannier90.mmn")
#~ print(M[0])
#~ print(M[-1])
#~ foo = list(enumerate(k_kplusb))
#~ foo2 = list(filter(lambda x: x[1][1]==12, foo))
#~ foo3 = sorted(foo2, key = lambda x: x[0])
#~ print(foo)
#~ print(foo2)
#~ print(foo3)

#~ for point in k_kplusb:
    #~ print(point)
#~ print(nntot)

