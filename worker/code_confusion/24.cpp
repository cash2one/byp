{
__try{
int division = 7;
for(int i=0;i<$a;++i) 
{
    if (i % 7 == 0)
	    division --;
    _confusion_sum /= division;
}
}
__except (EXCEPTION_EXECUTE_HANDLER){
    if (_confusion_sum % 7 == 0)
        _confusion_sum = 0xffffffff;
    else
        _confusion_sum = 0;
}
}
