{
    int a = 1;
    int b = 1;
    int c = 2;
    int iCount = 0;
    for (int i=0;i<$a;++i){
        c = a + b;
        a = b;
        b = c;
        _confusion_sum += c;
    }
    _confusion_sum += $a;
}
