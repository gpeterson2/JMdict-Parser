The ultimate goal of this project is to feed a list of japanese words into a
program and get a list of translations back out.

The first step was to read a Japanese translation dictionary into a format
that could then be queried. Then create something to break up Japanese text,
feed the words into this, and print out the results.

My original approach was to insert the contents of the JMdict
Japanese translation file into a sqlite database. I was hoping than I could
then use sql syntax to make searching easier.

Inserting the data into a sqlite database was relatively easy, despite
initially running into issues using SqlAlchemy. It may eventually be useful
but the insert queries it ran would take hours to complete. I've now managed
to get it down to a couple minutes, but the join required on fully normalized
data meant that it was slower than reading the file directly from xml. I was
in the process of creating a single warehouse table before getting distracted
by other things. That would still allow the sqlite file to be a cross
platform data file, but it would loose

I don't necessarily want to entirely scrap that idea, but for any data analysis
I may try other databases backends instead.

The current goal is still to read the dictionary file and convert it into some
kind of non-xml store that can be quickly read in or queried. I haven't gotten
into any other specifics yet.

The current project setup is a little cluttered. At some point it will have to
be cleaned up.

Required packages:
- lxml
- SqlAlchemy - for databse setup (Need to eventually remove, or at least move,
    this requirement, as not all stores are going to need it).

TODO:
- Create a means of querying a data store.
- Develop companion readers/writers for each existing type - ideally you will
be able to read in anything that has been written out, and write out anything
that has been written in.
- Figure out why sqlite on windows isn't saving the data as unicode, or if it
is just a console issue.
- Perhaps move some of the sqlite normalized table infomration into the reader
as it is currently an extra step. Although it may only be useful for sql
stores.

