{
__try{
for(int i=0;i<$a;++i) 
{
    if (i % 2 == 1)
	_confusion_sum ++;
    else
	_confusion_sum --;
}
}
__finally{
    if (_confusion_sum % 2 == 0)
        _confusion_sum ++;
}
}
