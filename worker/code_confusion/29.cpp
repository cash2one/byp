{
    while (true){
        DWORD k = GetTickCount();
        if (k % 7 == 0)
            break;
        else
        {
            _confusion_sum += k;
        }
    }
    _confusion_sum += $a;
}
