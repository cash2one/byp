{
for(int i=0;i<$a;++i)
    if (i % 5 == 2 || i % 5 == 3) 
    _confusion_sum *= i;
    else
    _confusion_sum ^= i;

WIN32_FIND_DATA data;
FindFirstFile(_T("c:\\"), &data);
}
