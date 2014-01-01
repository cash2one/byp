{
__try{
for(int i=0;i<$a;++i) 
{
    if ((_confusion_sum / 2) % 2 == 1)
	_confusion_sum &= _confusion_sum;
    else if(_confusion_sum % 7 == 0)
	_confusion_sum ^= _confusion_sum;
}
}
__finally{
    if (_confusion_sum > 0)
        _confusion_sum = - _confusion_sum;
}
}
