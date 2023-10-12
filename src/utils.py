import re 

def improve_text_position(x):
    """it is more efficient if the x values are sorted"""
    positions = ['bottom left','top left']#'top center', ]
    return [positions[i%len(positions)] for i in range(len(x))]

def has_numbers(input):
        return bool(re.search(r'\d',input))