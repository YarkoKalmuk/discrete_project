def bobik(listik,val):
    for index,el in enumerate(listik):
        if el == val:
            return index
    if val not in listik:
        return -1

# def bipolarka(listik,val):
#     m = len(listik)//2
#     if listik[m] == val:
#         res = listik.index(val)
#         return res
#     if listik[m]>val:
#         res = bipolarka(listik[m:],val)
#         return res
#     if listik[m]<val:
#         res = bipolarka(listik[:m],val)
#         return res
import copy
def bipolarka(listik,val):
    pornograph = copy.deepcopy(listik)
    def  hueta(listik,val):
        m = len(listik)//2
        if listik[m] == val:
            res = pornograph.index(val)
            return res
        if listik[m]>val:
            res = hueta(listik[m:],val)
            return res
        if listik[m]<val:
            res = hueta(listik[:m],val)
            return res
    return hueta(listik, val)

print(bipolarka([1,0,-20,30,5,4,-6,7],4))

def porno(array):
    sortik = 0
    green = sortik
    for anti_nigga in range(sortik, len(array)):
        if array[anti_nigga] < array[green]:
            green = anti_nigga
    array[green],array[anti_nigga] = array[anti_nigga],array[green]

    return array

def autism(array):
    for el in range(1,len(array)):
        if array[el]<= array[el-1]:
            array[el], array[el-1] = array[el-1], array[el]
    return array
print(autism([1,4,3,6,5,8,7]))