
import random as r
import os, os.path

def generate_otp():
    otp=""
    for i in range(6):
        otp += str(r.randint(1,9))
    print ("Your One Time Password is :" , otp)
    return otp



def verify_otp(input_otp):
    return True

def apply_pagination(cursor, page_num, page_size):
    """returns a set of documents belonging to page number `page_num`
        where size of each page is `page_size`.
        """
    # Calculate number of documents to skip
    skips = page_size * (page_num - 1)
    # Skip and limit
    cursor = cursor.skip(skips).limit(page_size)
    return cursor



def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, 'wb+')
