Preparation of form.csv:

1. Sort the google spreadsheet by REVERSE timestamp
    (What this does is, if people fill out the form twice, their latest response gets counted)

2. Make sure that the spreadsheet has the following format:
    column 1: Timestamp
    column 2: Name
    column 3: discord/phone
    column 4: Driver yes/no
    column 5: Number of seats if driver
    column 6: Will you need a ride yes/no
    2nd last column: dietary restrictions
    last column: comments/questions/concerns

3. Download the spreadsheet as a CSV file

4. Place it in the same folder as the groupifier.py file and name it 'form.csv'


Preparation of restrictions.txt:

Look at the example restrictions.txt file, and it will be self-explanatory.
Make sure that the file is named restrictions.txt.

If 3 people need to be together, enter like so:

y
a, b
y
a, c
y
b, c


How to run the program:

1. Install python. https://www.python.org/downloads/

2. Open the folder containing this file on windows explorer.

3. Make sure that you have the form.csv, restrictions.txt, officers.txt, big_instruments.txt files formatted correctly.

4. Right click, and then select "open in terminal"

5. Type "python groupifier.py", and then press enter.
