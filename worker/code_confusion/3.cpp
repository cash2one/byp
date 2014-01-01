{
for(int i=0;i<$a;++i) 
    _confusion_sum &= i;
    if (_confusion_sum < 0)
	_confusion_sum = -_confusion_sum * 5;
    if (_confusion_sum % 13 == 0)
	_confusion_sum = (int)GetCurrentProcess();
}
