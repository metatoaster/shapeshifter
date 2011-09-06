Shapeshifter Log to CSV Converter
=================================

A simple text entry to CSV converter.

This is named shapeshifter because it's named after name of the file
that was sent to me, `shapeshifter.txt`.  Its content was something
like this::

    #MARKERNAME
    IDENTIFIER-001
    #KEY1
    VALUE1
    #KEY2
    VALUE2
    #KEY3
    VALUE3
    #ENDMARKER
    #MARKERNAME
    IDENTIFIER-002
    ...
    #ENDMARKER
    #ENDQUEUE

Basically I was told I need to extract two fields from it and output it
as a table.  I thought it was going to be a simple five line script,
then I realized the party would prefer to have something to click at.

Hence the experiment to toy with TKinter came about.  Basically this is
a completely untested GUI app for Python, with some sort of purpose that
came along with it.  Again this started out as a five line script, so
there are no tests for it, therefore this program doesn't really exist
until some brave soul decides to write one for it.
