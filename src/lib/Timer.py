import time 
def timer(func) : 
    def dec(*args, **kwargs) : 
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"Time taken for operation : {end - start} seconds")
        return result
    return dec