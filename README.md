# soccer_lineup
#### Video Demo:  <URL HERE>
#### Description:
An application to help soccer coaches plan substitutions to ensure all players get equal playing time.

Technologies:
  - Python for server-side processing. 
  - The Django web framework (with HTML and JavaScript) to create the site.
  - A SQLite3 database.

To start, I created a virtual environment (python -m venv env). I then activated the virtual environment (source env/bin/activate) and added Django to that environment (pip install django). I then created a game_lineups django project (django-admin startproject game_lineups and python manage.py migrate). I've been using the development server to run the project (python manage.py runserver). When the development server is running, load http://127.0.0.1:8000/ in your browser to the application.
  
requirements.txt
  A text file that lists all the dependencies of the project and their versions.
  
env/
  
soccer_lineup/

Your README.md file should be minimally multiple paragraphs in length, and should explain what your project is, what each of the files you wrote for the project contains and does, and if you debated certain design choices, explaining why you made them.
