def remove_tag(tag, tag_tuple):
    new_tag_tuple = tag_tuple
    
    # se il secondo parametro è una stringa, lo tratta come una tupla
    if isinstance(tag_tuple, str) and tag==tag_tuple:
        return ()
    elif isinstance(tag_tuple, str):
        return (tag_tuple,)
    
    # controlla che il secondo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as second parameter, but "{type(tag_tuple)}" was found')
    
    # se la tupla ha il tag, lo rimuove
    if tag in tag_tuple: 
        tag_list = list(tag_tuple)
        tag_list.remove(tag)
        new_tag_tuple = tuple(tag_list)
        
    return new_tag_tuple

def append_tag(tag, tag_tuple):
    # se il secondo parametro è una stringa, lo tratta come una tupla
    if isinstance(tag_tuple, str):
        return (tag_tuple, tag)
    
    # controlla che il secondo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as second parameter, but "{type(tag_tuple)}" was found')
    
    # aggiunge il tag alla tupla
    tag_list = list(tag_tuple)
    tag_list.append(tag)
    new_tag_tuple = tuple(tag_list)
    
    return new_tag_tuple

def push_tag(tag, tag_tuple):
    # se il secondo parametro è una stringa, lo tratta come una tupla
    if isinstance(tag_tuple, str):
        return (tag_tuple, tag)
    
    # controlla che il secondo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as second parameter, but "{type(tag_tuple)}" was found')
    
    # aggiunge il tag alla tupla
    tag_list = list(tag_tuple)
    tag_list.insert(0,tag)
    new_tag_tuple = tuple(tag_list)
    
    return new_tag_tuple

def has_tag(tag_tuple, tag):   
    # controlla se il primo parametro è una stringa
    if isinstance(tag_tuple, str):
        return tag==tag_tuple
    
    # controlla che il primo parametro sia una tupla
    if not isinstance(tag_tuple,tuple):
        raise TypeError(f'expected a tuple as first parameter, but "{type(tag_tuple)}" was found')
        
    # controlla se è presente il tag
    return tag in tag_tuple

def is_even(n):
    return int(n)%2==0

def is_number(n):
    try:
        float(n)
        int(n)    
    except ValueError:
        return False
    
    return True