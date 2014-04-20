=============
JMdict Parser
=============

-----
Goals
-----

The ultimate goal of this project is to be a library which can be feed
a list of Japanese words and return a list of translations. Ideally without
requiring a separate service running such as a database or mongodb.

------
Issues
------

My original approach was to insert the contents of the JMdict
Japanese translation file into a sqlite database.

Using SqlAlchemy was relatively easy, but at that point bulk insertions
would take a significant amount of time, twenty minutes or more, to load.
Removing SqlAlchemy cut that down to a couple less than a minute  but
required in-line sql statements, meaning it was no longer portable (or as
portable as possible).

The next problem was that the joins required on fully normalized
data meant that sqlite is slower than reading the file directly from xml.
I was in the process of creating a single warehouse table before getting
distracted and losing interest.

I don't necessarily want to entirely scrap sqlite, but may try other
databases backends instead.

The current goal is still to read the dictionary file and convert it into some
kind of non-xml store that can be quickly read in or queried. At this point
the specifics are fairly vague.

------------
Requirements
------------
- lxml
- SqlAlchemy - not currently being used.

-----
TODO:
-----

- Create a settings file that can be used for multiple databases or whatever
  else comes along.
- Create an interface for querying a data store.
- Develop companion readers/writers for each data type - ideally you will
  be able to read in anything that has been written out, and write out anything
  that has been written in. For example there should be an edict to JMdict, or
  vice versa (at the very least for testing purposes).
- Support other possible backends. The original goal was for this to be used
  as a generic desktop application, so mongo was out. It would however make
  storing an querying the data far easier and would be perfect for a web
  application.

