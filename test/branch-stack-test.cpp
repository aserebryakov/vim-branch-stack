int main() { // Function start
    int switchvar = 42;

#if 1
    if (true) // New branch
    {
        if (false) {
            // Do something
            if (true)
                x = 42;
            else
                x = 400;
            x = 500;
        }
        else {
            // Awesomely elsed
        }

        try {
            // Throw exception
        }
        catch (...)
        {
            // Awesomely catched
        }
        x = 500;
    }
#else
#endif
    while ((true))
    {
#define INFINITE_LOOP while(true) {
        for (int i = 0; i < 42; i++)
        {
            // Checking if this comment affects the parsing
            // for while, switch, try, else if, case, default, catch

            if (true || "test" ||
                false)
            {
                // Do something
            }
            else if (x == true || y != '0') // Alternative branch
            {
                try {
                    if (true)
                        x = 42;
                    else
                        x = 400;
                }
                catch (Exception e)
                {
                    if (true)
                        x = 42;
                    else
                        x = 400;
                }
                catch (...)
                {
                    // Awesomely catched
                }
                x = 500;
            }
            else if (x == true) // Another alternative branch
            {
                if (true) foo();

                if (true)
                    foo();
                else if (true)
                    bar();
                else
                    test = baz;

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
                            break;
                        case 3:
                        default:
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
