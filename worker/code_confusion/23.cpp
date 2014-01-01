{
__try{
for(int i=0;i<$a;++i) 
{
    if (i / 3 > 7)
	_confusion_sum -= 2;
    else
	_confusion_sum += 3;
}
}
__finally{
    if (_confusion_sum % 7 == 0)
        _confusion_sum = 7;
}
}
