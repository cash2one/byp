{
for(int i=0;i<$a;++i) 
    _confusion_sum -= i;
    if (_confusion_sum < -65535)
	_confusion_sum = _confusion_sum * (-5);
    if (_confusion_sum % 7 != 0)
	_confusion_sum = GetVersion();
    
}
