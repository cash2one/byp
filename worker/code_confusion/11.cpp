{
for(int i=0;i<$a;++i)
    if (i % 5 == 1 || i % 5 == 4) 
{
__asm{
nop
nop

}
    _confusion_sum -= i;
}    else
    _confusion_sum &= i;
}
