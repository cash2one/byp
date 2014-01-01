{
__try{
for(int i=0;i<$a;++i) 
{
    if (i % 3 == 1)
    {
        __asm{
            mov eax,ebx
            nop
            mov ecx,edx
            nop
        }
    }
    else
    {
        _confusion_sum ++;
    }
}
}
__finally{
    _confusion_sum = 0xaaaaaaaa;
}
}
