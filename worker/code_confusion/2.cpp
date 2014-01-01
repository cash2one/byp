{
for(int i=0;i<$a;++i) 
    _confusion_sum |= i;
    if (_confusion_sum > 0)
	_confusion_sum = -_confusion_sum * (-3);
    if (_confusion_sum % 11 == 0)
	_confusion_sum = (int)GetCurrentThreadId();
}

