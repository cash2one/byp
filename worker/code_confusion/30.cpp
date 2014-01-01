{
    int iCount = 0;
    while (true){
        DWORD k = GetTickCount();
        if (k % 3 == 0)
            break;
        else
        {
            _confusion_sum *= iCount++;
        }
    }
    _confusion_sum += $a;
}
