# coding=UTF-8
"""
@author tomas
@date    2013-03-31
@desc
    
    
@brief
     
"""

class worker():
    pass

class manager():
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super().__new__(cls, *args, **kwargs)
            return cls._inst
        
    def __init__(self, *args, **kwargs):
        pass
