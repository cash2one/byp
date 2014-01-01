{
	TCHAR szBuf[] = _T("abcdefghijklmnopqrstuvwxyz1234567890");
	srand( (unsigned)time( NULL ) );
	int i=1;
	while(i++<1000)
	{
		if (szBuf[rand()%36] == 'a') break;
	}
}