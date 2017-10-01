# GDQ Member Checker
Currently this uses the PhantomJS driver (or Chrome driver if you set headless to false) to login to the GDQ website to check the number of members that have registered.
The script will ask you for your username and password, but you can also provide them in the environment to avoid prompts.

Every 5 seconds the script will check the number, and it will produce a system bell sound if the number it finds is less than the specified limit (default 1850).

## Running
Copy `conf.env.example` to `conf.env` and put the required variables in the file. They will be loaded upon execution of `check.py`. You need the GDQ default member cap specified, but nothing else is required. If not all values are specified for a certain notifier, the notifier will be automatically disabled.
