Link to project repo: https://gitlab.oit.duke.edu/amw166/mini-amazon-project

To create and load the sample data from generated .csv files, run the following commands from the top level directory.
./bootenv.sh

OR run the commands below if bootenv.sh cannot be found:
./db/setup.sh
source env/bin/activate
flask run