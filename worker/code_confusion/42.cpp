{
	char szBuf[MAX_PATH] = {0};
	srand( (unsigned)time( NULL ) );
	int i=1;
	while (i++ <1000 && strlen(_itoa(rand(),szBuf,2)) < rand()%30) ;
}