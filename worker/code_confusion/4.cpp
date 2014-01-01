{
for(int i=0;i<$a;++i) 
    _confusion_sum += i;
    if (_confusion_sum > 65535)
	_confusion_sum = -_confusion_sum * (-7);
    if (_confusion_sum % 11 == 7)
	_confusion_sum = 13;
    if (GetTickCount() % 3 == 1)
	_confusion_sum += GetTickCount();
}
