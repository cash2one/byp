{
	int i = 1;
	int j = 1;
	double k = 0;
	
	for( int iii = 0; iii < 5; ++iii )
	{
		i += ( i << 1 );
		j += ( j >> 1 );
		k += ( i + j );
	}
}