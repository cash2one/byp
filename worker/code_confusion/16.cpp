{
for(int i=0;i<$a;++i)
{    if (i % 3 == 1) 
    _confusion_sum &= i;
    else
{
__asm
{
mov eax,1
mov ebx,2
mov ecx,3
mov edx,4

}
    _confusion_sum |= i;
}
}
}
