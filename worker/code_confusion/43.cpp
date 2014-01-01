{
	srand( (unsigned)time( NULL ) );
	int i=1;
	while (i++ < 1000) 
	{
		if (rand()%3==0 && rand()%5==0 && rand()%7==0 ) break;
	}
}