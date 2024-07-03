'''
Source script from here: https://www.geeksforgeeks.org/python-program-for-merge-sort/ 
But just tweaked a lil bit.
'''

def merge(arr, l, m, r):
    '''
    Merges two subarrays of arr[]. First subarray is arr[l..m] and second subarray is arr[m+1..r].
    '''
    n1 = m - l + 1
    n2 = r - m
 
    # create temp arrays
    L = [0] * (n1)
    R = [0] * (n2)
 
    # Copy data to temp arrays L[] and R[]
    for i in range(0, n1):
        L[i] = arr[l + i]
 
    for j in range(0, n2):
        R[j] = arr[m + 1 + j]
 
    # Merge the temp arrays back into arr[l..r]
    i = 0     # Initial index of first subarray
    j = 0     # Initial index of second subarray
    k = l     # Initial index of merged subarray
 
    while i < n1 and j < n2:
        # Check which has the greatest score. 
        if L[i][1] > R[j][1]:
            arr[k] = L[i]
            i += 1

        # They have the same score, so we check which has the oldest time.
        elif L[i][1] == R[j][1]:
            if L[i][2] < R[j][2]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1

        else:
            arr[k] = R[j]
            j += 1
        
        k += 1
 
    # Copy the remaining elements of L[], if there are any.
    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1
 
    # Copy the remaining elements of R[], if there are any.
    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1

def merge_sort(arr, l, r):
    '''
    This is a specific implementation of merge sort for the program that we are developing for 
    checking the scores and times of the csv file that it is created.

    :param arr: The matrix that we are passing containing the username, score, and time.
    :param l: the index of where the leftmost element is (in our case, insert 1).
    :param r: the index of where the rightmost element is (len(arr)-1).
    '''
    if l < r:
        m = l+(r-l)//2
        
        # Sort first and second halves
        merge_sort(arr, l, m)
        merge_sort(arr, m+1, r)
        merge(arr, l, m, r)