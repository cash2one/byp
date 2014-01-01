{
   DWORD dwID= GetCurrentThreadId();
   for (int i =0; i<$a; i++)
   {
       if ( 0 == dwID%2)
       {
	  continue;
       }
       else
       {
	  dwID += 1;
       }
       dwID -= 2;
    }
}