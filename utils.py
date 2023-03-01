def find_index(check_list, check_func):
    r = list(i for i, v in enumerate(check_list) if check_func(v))
    if (len(r) == 0):
        return -1
    return r[0]