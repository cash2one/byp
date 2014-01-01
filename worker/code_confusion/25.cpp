{
__try{
 char *pinval = (char*)0xffffffff;
for(int i=0;i<$a;++i) 
{
    if (i % 37 == 0)
	    _confusion_sum = *pinval;
    _confusion_sum ++;
}
}
__except (EXCEPTION_EXECUTE_HANDLER){
    _confusion_sum = 0xcccccccc;
}
}
