# mx_random
mx_random is a [PyPlanet](https://github.com/PyPlanet/PyPlanet/) app/plugin that selects a random map from [ManiaExchange](https://tm.mania.exchange/) and adds a ranking system to it. 

## How it works
The plugin takes a random map from ManiaExchange and puts it on the server. There is no timelimit on the map, however as soon as a player gets author medal, the timelimit is set to 20 seconds, and that player gets 1 point. Other players have these 20 seconds to try and get the author medal as well. The amount of points they get halves every time someone finishes with author medal. As such, the first to finish gets 1 point, the second 0.5, the third 0.25, etc. These points are global and the ranking can be seen using the in-game button in the bottom right, or with the command /mxrrank. A help message is also available in-game with a button or the command /mxrhelp.

## Supported games and environments
While this plugin was developed for a Maniaplanet TMAll server, it can easily be ported to another environment or TM2020.
Porting this to ShootMania Obstacle (or any other "racing-like" modes) could probably be done as well but with a bit more work.
In `__init__.py`, at [line 50](https://github.com/LinUwUxCat/pyplanet_mx_random/blob/main/__init__.py#L50), you can find a web request to [tm.mania.exchange/mapsearch2/search?api=on&random=1](https://tm.mania.exchange/mapsearch2/search?api=on&random=1), followed by a bunch of `tpack` values.
If you only have e.g. a Canyon server, you'd want to only leave `tpack=TMCanyon`. Similarly, if you want to add another titlepack like e.g. the competition titlepack, you'll want to put `tpack=esl_comp` in there.
For TM2020, you'll want to change the url to be `trackmania.exchange`, and you can remove the titlepacks.

## How to install
After installing PyPlanet, create an `apps` folder in your pyplanet server directory, and clone this repo in it: 
```
git clone https://github.com/LinUwUxCat/pyplanet_mx_random
```