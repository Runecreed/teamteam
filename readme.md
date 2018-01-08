To use the project:

Install Python to your PC, make sure the path variable to python exists
( check by running a command line and writing python) --> this should not cause any errors

then, install pipenv if you do not have it yet, do so by running the command:

pip install pipenv

Now you have the pipenv tool installed and you can use it to update your dependencies for the project

To do so:
First clone the repository // Pull from the repository

notice that there is a PipFile and PipFile.lock in the root of the project, this holds dependencies for pipenv to install

install them by opening a command line (terminal/shell/cmd) in the root folder of the project ---> $....../teamteam/
and run the command

pipenv install


this will now create a virtual environment if none exists yet, and install the dependencies for you to run the project.
In practice this should install Django 2.0.1 and the requests library on first launch


