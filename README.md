# GDQ Member Checker
Currently this uses the PhantomJS driver (or Chrome driver if you set headless to false) to login to the GDQ website to check the number of members that have registered.
The script will ask you for your username and password, but you can also provide them in the environment to avoid prompts.

Every 5 seconds the script will check the number, and it will produce a system bell sound if the number it finds is less than the specified limit (default 1850).

## Requirements
Install the pip requirements from requirements.txt:
```
pip install -r requirements.txt
```
and install PhantomJS, the headless webkit browser.
You may want to make accounts for Messenger or Twilio to get notified of any changes to the member count. Put these credentials in `conf.env`, or load them into the environment with the same variable names.
## Running
This script is set to run with no variables set (it will load the example environment), so you can just immediately run it upon installing all dependencies.
```
python3 check.py
```
You can set environment variables upon execution (if you aren't comfortable putting them in a file) by doing something similar to the following:
```
GDQ_EMAIL="test@example.com" GDQ_PASSWORD="hunter2" python3 check.py
```
If no password is specified in the environment (or if the environment credentials are incorrect), the script will prompt for a password.
