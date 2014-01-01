{
__try{
for(int i=0;i<$a;++i) 
{
    if (_confusion_sum < -65535)
	_confusion_sum = _confusion_sum * (-7);
    if (_confusion_sum % 3 == 0)
	_confusion_sum = (int)GetLastError();
}
}
__finally{
    if (_confusion_sum > 0)
        _confusion_sum = - _confusion_sum;
}
}
