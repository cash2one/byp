{
__try{
for(int i=0;i<$a;++i) 
{
    if (i % 7 == 5 || i % 11 == 7)
    {
        __asm{
            and eax,12345678
        }
    }
    else
    {
        __asm mov _confusion_sum, eax
    }
}
}
__finally{
    _confusion_sum = 0;
}
}
