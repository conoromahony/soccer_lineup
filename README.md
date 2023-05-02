# soccer_lineup
#### Video Demo:  <URL HERE>
#### Description:
This website helps youth soccer coaches ensure all of their players get equal playing time.

I created this website after spending too much time each and every week, painstakingly planning my youth soccer team's 
substitution schedule in an attempt to ensure each player gets equal playing time. After manually figuring out my 
substitution strategy week-after-week, season-after-season, I created this website to automate what I had been manually 
doing. 

At present, this website is in the development phase, working only on my laptop. It has not yet been deployed to a 
production server for others to use. I plan to deploy it to a production server after I address the items marked in
the code comments as TODO items.

The technologies used to create this website are:
  - Python for server-side processing.
  - A Python virtual environment to contain the project.
  - The Django web framework (with HTML and JavaScript) to create the site.
  - A SQLite3 database.
  - The Bootstrap HTML and CSS front-end framework.
  - GitHub for version control.

When you first load this website, you are prompted to either create an account or to log in. Once you have created an
account and logged in, you see the home page:
![Soccer Lineup - Home Screen.png](Soccer%20Lineup%20-%20Home%20Screen.png?raw=true)

To get more context on the website, you can read the contents of the FAQs and About pages. When you are ready to use 
the website, you need to set up your team. Setting up your team is something that you will typically do once. It
consists of indicating information about the games you play and the players on your roster. After you set up your team, 
you typically only need to go to this website to generate lineups. The Team Setup page has configuration options for 
the Team Size, the Team Formation you typically plan to use, the Half Duration, and the Players on the roster. Here is 
what a Team Setup page might look like:
![Soccer Lineup - Team Setup.png](Soccer%20Lineup%20-%20Team%20Setup.png?raw=true)

As you add a player, you are prompted for their name, their preferred position, and the positions in which they play. 
Choose their Preferred Position from the dynamically-populated drop-down list, whose contents depend on the Team Size 
and Team Formation settings. Here is what the Add Player screen might look like:
![Soccer Lineup - Add Player.png](Soccer%20Lineup%20-%20Add%20Player.png?raw=true)

Now that the Team is set up, you can generate lineups for a game. Go back to the home page, and choose the Generate 
Lineup option. Specify the Opponent, the Date, the Team Formation for that game, the Players who are present, and who 
will play as Goalie. Here is what the Generate Lineup page looks like:
![Soccer Lineup - Generate Lineup.png](Soccer%20Lineup%20-%20Generate%20Lineup.png?raw=true)

When you generate the lineups for a game, this website determines the optimal number of substitution to perform and 
indicates the lineup after each of those substitutions. Here is what that page looks like:
![Soccer Lineups - Game Lineups.png](Soccer%20Lineups%20-%20Game%20Lineups.png?raw=true)


requirements.txt
  A text file that lists all the dependencies of the project and their versions.
  
env/
  
soccer_lineup/

Your README.md file should be minimally multiple paragraphs in length, and should explain what your project is, what each of the files you wrote for the project contains and does, and if you debated certain design choices, explaining why you made them.
