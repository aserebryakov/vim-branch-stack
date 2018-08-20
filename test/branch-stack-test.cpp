int main() { // Function start
    int switchvar = 42;

#if 1
    if (true) // New branch
    {
        // Do something
    }
#else
#endif
    while (true)
    {
        for (int i = 0; i < 42; i++)
        {
            if (true)
            {
                // Do something
            }
            else if (x == true) // Alternative branch
            {
                if (y == false) { // Nested branch
                    // Do something
                }
                else // Nested alternative
                {
                    switch (switchvar)
                    {
                        case 1:
                        {
                            break;
                        }
                        case 2:
                        {
                            break;
                        }
                    }
                    // Do something
                }
                // Do something
            }
            else // Alternative branch
            {
                // Do someting else
            }
        }
    }

    return 0;
}
