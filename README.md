# CarReliability
Using image processing and webscraping combined with the EPA database to get reliability of cars alongside their MPG

From my work I have found (to my knowledge) that the best cars wtih >90 reliability ranking on https://www.dashboard-light.com/ and a >30 MPG Combined MPG on the EPA database are the following:

Honda Accord - 2018
Honda Civic - 2012-2014
Honda CR-Z - 2011-2012
Honda Fit - 2009-2013, 2016-2018
Honda Insight - 2011
Nissan Leaf - 2011-2012, 2013-2015
Toyota Camry - 2018
Toyota Corolla - 2004, 2006-2008, 2014-2018
Toyota Prius - 2006-2010, 2011-2017
Toyota Yaris - 2007-2012, 2013, 2017
Volkswagen Beetle - 2014-2015
Volkswagen Golf - 2012, 2015
Volkswagen Jetta - 2018

Hopefully this helps out someone who had the same damn question that I did.
Note that the Nissan Leaf has terrible range.

Update 2025:
This code is useful for lots of things, anywhere data is being hidden behind a graph. I'm going to rework this code:
- Clean it up, so it's cleaner and more understandable
- Add seperate files that call the main files like a library (for cars/pcParts)
- generify main files so different scripts can be run to yoink different data
- Add a github actions file (or similar) so that every so often new data is pulled in, and errors alerted to
- New github action to re-parse and update the data
- New github action so that the new data is always up to date
- New github action to make a d3 graph (ideally, or Plotly Graph) so that the data is easily parsible
