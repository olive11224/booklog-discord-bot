#Cat Photos from https://github.com/AtharvaTaras/Cat-Images-Dataset
import discord
from discord.ext import commands
import json
import os
from datetime import datetime, date
import calendar
import random

sampleJSON = '' #Path of JSON file where data is stored
catPhotosFolder = '' #Path of folder with cat photos to bring burst of dopamine
catPhotos = os.listdir(catPhotosFolder)


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, description = 'A bot to keep reading logs and reach reading goals.')

if os.path.exists(sampleJSON) and os.path.getsize(sampleJSON) == 0:
    with open(sampleJSON, 'w') as f:
        f.write('{}')

def load_data():
    with open(sampleJSON, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(sampleJSON, 'w') as f:
        json.dump(data, f, indent=2)

#BASIC COMMANDS

@bot.command(help = 'Register a booklog for yourself.')
async def register(ctx):
    """
    `!register`
    Registers a booklog for the user under their Discord username.
    """
    username = ctx.author.name
    try:
        data = load_data()
        if username in data:
            raise Exception('This person is already registered!')
        data[username] = {'books': []}
        save_data(data)
        await ctx.send(f"User '{username}' registered successfully.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Add a book to your book log.')
async def addBook(ctx, *, args):
    """
    Format `!addBook <title>, <author>, <page count>, <start date>, <end date>`.

    Example:

    `!addBook The Idiot, Fyodor Dostoyevsky, 345, 2025-03-04, 2025-06-12`
    """
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        if len(parts) == 0:
            raise Exception("You must provide at least a title.")
        title = parts[0]
        author = parts[1] if len(parts) > 1 else ""
        pageCount = parts[2] if len(parts) > 2 else ""
        startDate = parts[3] if len(parts) > 3 else ""
        endDate = parts[4] if len(parts) > 4 else ""
        data = load_data()
        if username not in data: #Not already registered
            data[username] = {'books': []}
        if any(book['title'] == title and book['author'] == author for book in data[username]['books']):
            raise Exception('You have already logged this book.')
         #Add the book
        data[username]['books'].append({
        'title': title,
        'author': author,
        'page count': pageCount,
        'start date': startDate,
        'end date': endDate
        })
        save_data(data)
        await ctx.send(f"Book '{title}' added for user {username}.")
        if endDate != '' and 'reading goal deadline' in data[username]:
            deadline = data[username]['reading goal deadline']
            booksInDateRange = [book for book in data[username][books] if book['end date'][:7] == deadline[:7]]
            if len(booksInDateRange) >= int(data[username]['reading goal']):
                randomCatPhoto = random.choice(catPhotos)
                imagePath = os.path.join(catPhotosFolder, randomCatPhoto)
                await ctx.send(f"{username} has reached their monthly reading goal! 🎉🎉🎉")
                await ctx.send(file=discord.File(imagePath))
                del data[username]['reading goal']
                del data[username]['reading goal deadline']
                save_data(data)
                await ctx.send(f"The reading goal for this month has been removed. See you next month!")
            
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help='Remove a book from your book ךog.')
async def removeBook(ctx, *, args):
    '''Use either `!removeBook <title>` or `!removeBook <title>, <author>` to remove a book from your bookLog.
    '''
    try:
        parts = [p.strip() for p in args.split(',')]
        title = parts[0] 
        if len(parts) == 2: #If author is specified
            author = parts[1]
        else:
            author = '' #If author is not specified
        data = load_data()
        username = ctx.author.name
        books = data[username]['books']
        candidateBooks = [book for book in books if book['title'] == title]
        if len(candidateBooks) == 1: #There's only one book with the same title
            if candidateBooks[0]['author'] == author or author == '': #If the author matches or was not given
                books.remove(candidateBooks[0])
                save_data(data)
                if title != '': #If there is an author
                    await ctx.send(f"The book {title} by {candidateBooks[0]['author']} has been removed from your booklog.")
                else:
                    await ctx.send(f"The book {title} has been removed from your booklog.") #If there isn't one
            elif candidateBooks[0]['author'] != author: #If the author doesn't match
                raise Exception('There is no book in your booklog with the specified title and author.')
        if len(candidateBooks) > 1: #If there's multiple books with the same title
                candidateBooksAuthors = [book for book in candidateBooks if book['author'] == author] #Books with the same title-author combo
                if len(candidateBooksAuthors) == 1: #If there's only one of such book
                    books.remove(candidateBooksAuthors[0])
                    save_data(data)
                    if title != '': #If there's an author
                        await ctx.send(f"The book {title} by {author} has been removed from your booklog.")
                    else: #If there's no author
                        await ctx.send(f"The book {title} has been removed from your booklog.")
                else:
                    raise Exception('There are multiple books in your booklog with the specified author and title. This is very strange and please tell Olive11224.')
        if len(candidateBooks) ==0: #There's no book with the same title
            raise Exception('There is no book in your booklog with the specified title.')
    except Exception as e:
        await ctx.send(f"❌ {e}")

#READING GOAL RELATED
@bot.command(help = 'Add or change your personal monthly reading goal.')
async def addReadingGoal(ctx, readingGoal):
    '''
    Use `!addReadingGoal <# of books>` to add/update your monthly reading goal.
    '''
    try:
        data = load_data()
        username = ctx.author.name
        data[username]['reading goal'] = readingGoal
        today = datetime.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        readingGoalDeadline = date(today.year, today.month, last_day).isoformat()
        data[username]['reading goal deadline'] = readingGoalDeadline
        save_data(data)
        bookWord = 'book' if readingGoal == 1 else 'books'
        await ctx.send(f'You will work toward reading {readingGoal} {bookWord} by {readingGoalDeadline}.')
        booksInDateRange = [book for book in data[username]['books'] if book['end date'][:7] == readingGoalDeadline[:7]]
        if len(booksInDateRange) >= int(data[username]['reading goal']):
                randomCatPhoto = random.choice(catPhotos)
                imagePath = os.path.join(catPhotosFolder, randomCatPhoto)
                await ctx.send(f"{username} has reached their monthly reading goal! 🎉🎉🎉")
                await ctx.send(file=discord.File(imagePath))
                del data[username]['reading goal']
                del data[username]['reading goal deadline']
                save_data(data)
                await ctx.send(f"The reading goal for this month has been removed. See you next month!")
    except Exception as e:
        await ctx.send(f"❌ {e}")

#INFORMATIONAL COMMANDS
@bot.command(help = 'Get the number of books on your or someone else\'s book log.')
async def getNumberofBooks(ctx, username = ''):
    """
    Write either `!getNumberofBooks` to get the number of books in your own booklog or `!getNumberofBooks <username>` to get someone else's.
    """
    if username == '':
        username = ctx.author.name
    try:
        data = load_data()
        number = len(data[username]['books'])
        book_word = 'book' if number == 1 else 'books'
        await ctx.send(f"{username} has read {number} {book_word}.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Get the number of books you or someone else has finished reading.')
async def getNumberCompletedBooks(ctx, username = ''):
    """
    Write either `!getNumberCompletedBooks` to get the number of books you have read or `!getNumberCompletedBooks <username>` for someone else.
    """
    if username == '':
        username = ctx.author.name
    try:
        data = load_data()
        number = len([p for p in data[username]['books'] if p['end date'] != ''])
        book_word = 'book' if number == 1 else 'books'
        await ctx.send(f"{username} has finished reading {number} {book_word}.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Get descriptions of each book in someone\'s book log.')
async def getBooks(ctx, username = ''):
    '''
        If you want to get your own book log data, simply type `!getBooks`. 
        Otherwise, specify a username with `!getBooks <username>`.
    '''
    try:
        if username == '':
            username = ctx.author.name
        data = load_data()
        books = data[username]['books']
        if not books:
            await ctx.send(f"{username} has not read any books yet!")
            return
        messages = [f'These are the books read or being read by {username}. \n']
        for i, book in enumerate(books, 1):
            #messages.append(f"{i}. {book['title']} by {book['author']}, with {book['page count']} pages. Started {book['start date']} and ended {book['end date']}.")
            messages.append(f"{i}. {book['title']}")
            if book['author']:
                messages.append(f" by {book['author']}")
            if book['page count']:
                messages.append(f", with {book['page count']} pages")
            messages.append(f".\n\t")
            if book['start date'] and book['end date']:
                messages.append(f"Started {book['start date']} and ended {book['end date']}.")
            elif book['start date']:
                messages.append(f"Started {book['start date']}.")
            elif book['end date']:
                messages.append(f"Ended {book['end date']}.")
            messages.append('\n')
        await ctx.send(''.join(messages))
    except Exception as e:
        await ctx.send(f"❌ {e}")

#UPDATE COMMANDS
@bot.command(help = 'Add an author to a book title you have not previously done so to.')
async def addAuthor(ctx, *, args):
    """
        Use  `!addAuthor <title> <author>` to set an author for a book. 
    """
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        title = parts[0] 
        author = parts[1] 
        data = load_data()
        booksWithTitle = [d for d in data[username]['books'] if d['title'] == title]
        if len(booksWithTitle) ==0:
            raise Exception('No books by this title found.')
        if len(booksWithTitle) > 1:
            raise Exception('Multiple books found with this title.')
        old_author = booksWithTitle[0].get('author', '') #Saves the old author, giving an empty string if there isn't any.
        booksWithTitle[0]['author'] = author #Updates author
        save_data(data)
        if old_author:
            await ctx.send(f"Changed the author of '{title}' from {old_author} to {author}.")
        else:
            await ctx.send(f"Set the author of '{title}' as {author}.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help='Add a beginning date to a book in your booklog.')
async def addStartDate(ctx, *, args):
    ''' Use either `!addStartDate <title> <startDate> <author>` or `!addStartDate <title> <startDate>` to set a day when you started reading a book.
    '''
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        title = parts[0]
        if len(parts) == 3:
            author = parts[2]
        if len(parts) >3 or len(parts) < 2:
            raise Exception('Wrong number of arguments.')
        startDate = parts[1]
        data = load_data()
        books = data[username]['books']
        CandidateBooks = [book for book in books if book['title'] == title]
        if len(parts) == 2: #Did not input author
            if len(CandidateBooks) == 0: #No books with this title
                raise Exception('No book found with this title.')
            elif len(CandidateBooks) > 1: #Multiple books with this title.
                raise Exception('Multiple books found with this title. Please specify an author.')
            elif len(CandidateBooks) == 1: #Exactly one book found. Update.
                CandidateBooks[0]['start date'] = startDate
                save_data(data)
                await ctx.send(f'You started {title} on {startDate}.')
        if len(parts) == 3: #Inputted author
            if len(CandidateBooks) == 0: #No book with this title
                raise Exception('No book found with this title.')
            elif len(CandidateBooks) == 1:#One book with this title
                if CandidateBooks[0]['author'] == author: #author matches
                    CandidateBooks[0]['start date'] = startDate
                    save_data(data)
                    await ctx.send(f'You started {title} on {startDate}')
                elif CandidateBooks[0]['author'] == '': #author of book is missing
                    CandidateBooks[0]['author'] = author #Fill in author
                    CandidateBooks[0]['start date'] = startDate
                    save_data(data)
                    await ctx.send(f'Setting the author of {title} as {author}. \n You started it on {startDate}.')
                else: #author doesn't match
                    raise Exception(f'There is no book logged entitled {title} and written by {author}.')
            elif len(CandidateBooks) >1: #Mutliple books with same title
                CandidateBooksAuthors = [book for book in CandidateBooks if book['author'] == author] #Filter for books with the same author
                if len(CandidateBooksAuthors) == 0: #Title-author combo doesn't match
                    raise Exception(f'There is no book logged entitled {title} and written by {author}.')
                elif len(CandidateBooksAuthors) == 1: #Title-author combo matches one book
                    CandidateBooksAuthors[0]['start date'] = startDate
                    save_data(data)
                    await ctx.send(f'You started {title} by {author} on {startDate}.')
                elif len(CandidateBooksAuthors) > 1: #Title-author combo matches multiple books
                    raise Exception(f'There are multiple books logged entitled {title} and written by {author}.')
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Add an ending date to a book in your booklog.')
async def addEndDate(ctx, *, args):
    """
        Use either `!addEndDate <title> <endDate> <author>` or `!addEndDate <title> <endDate>` to set a day when you started reading a book.
    """
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        title = parts[0]
        if len(parts) == 3:
            author = parts[2]
        if len(parts) >3 or len(parts) < 2:
            raise Exception('Wrong number of arguments.')
        endDate = parts[1]
        data = load_data()
        books = data[username]['books']
        CandidateBooks = [book for book in books if book['title'] == title]
        if len(parts) == 2: #Did not input author
            if len(CandidateBooks) == 0: #No books with this title
                raise Exception('No book found with this title.')
            elif len(CandidateBooks) > 1: #Multiple books with this title
                raise Exception('Multiple books found with this title. Please specify an author.')
            elif len(CandidateBooks) == 1: #Exactly one book with this title
                CandidateBooks[0]['end date'] = endDate
                save_data(data)
                await ctx.send(f'You completed {title} on {endDate}.')
        if len(parts) == 3: #Inputted author
            if len(CandidateBooks) == 0: #No books with this title
                raise Exception('No book found with this title.')
            elif len(CandidateBooks) == 1: #One book with this title
                if CandidateBooks[0]['author'] == author: #Author matches
                    CandidateBooks[0]['end date'] = endDate
                    save_data(data)
                    await ctx.send(f'You completed {title} on {endDate}')
                elif CandidateBooks[0]['author'] == '': #Author empty
                    CandidateBooks[0]['author'] = author
                    CandidateBooks[0]['end date'] = endDate
                    save_data(data)
                    await ctx.send(f'Setting the author of {title} as {author}. \n You completed it on {endDate}.')
                else: #author doesn't match
                    raise Exception(f'There is no book logged entitled {title} and written by {author}.')
            elif len(CandidateBooks) >1:
                CandidateBooksAuthors = [book for book in CandidateBooks if book['author'] == author]
                if len(CandidateBooksAuthors) == 0: #No book matching title-author combo
                    raise Exception(f'There is no book logged entitled {title} and written by {author}.')
                elif len(CandidateBooksAuthors) == 1: #One book matching title-author combo
                    CandidateBooksAuthors[0]['end date'] = endDate
                    save_data(data)
                    await ctx.send(f'You completed {title} by {author} on {endDate}.')
                elif len(CandidateBooksAuthors) > 1: #Multiple books matching title-author combo
                    raise Exception(f'There are multiple books logged entitled {title} and written by {author}.')
        if 'reading goal deadline' in data[username]:
            deadline = data[username]['reading goal deadline']
            booksInDateRange = [book for book in data[username]['books'] if book['end date'][:7] == deadline[:7]]
            if len(booksInDateRange) >= int(data[username]['reading goal']): #Reading goal met
                randomCatPhoto = random.choice(catPhotos)
                imagePath = os.path.join(catPhotosFolder, randomCatPhoto)
                await ctx.send(f"{username} has reached their monthly reading goal! 🎉🎉🎉")
                await ctx.send(file=discord.File(imagePath))
                del data[username]['reading goal'] #Clear reading goal data
                del data[username]['reading goal deadline']
                save_data(data)
                await ctx.send(f"The reading goal for this month has been removed. See you next month!")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Add a page count to a book in your booklog.')
async def addPageCount(ctx, *, args):
    '''
    Use either `!addPageCount <title> <pageCount> <author>` or `!addStartDate <title> <pageCount>` to set the number of pages for a book.
    '''
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        title = parts[0]
        if len(parts) == 3:
            author = parts[2]
        if len(parts) >3 or len(parts) < 2:
            raise Exception('Wrong number of arguments.')
        pageCount = parts[1]
        data = load_data()
        books = data[username]['books']
        CandidateBooks = [book for book in books if book['title'] == title]
        if len(parts) == 2: #Did not input author
            if len(CandidateBooks) == 0: #No books with this title
                raise Exception('No book found with this title.')
            elif len(CandidateBooks) > 1: #Multiple books with this title.
                raise Exception('Multiple books found with this title. Please specify an author.')
            elif len(CandidateBooks) == 1: #Exactly one book found. Update.
                CandidateBooks[0]['page count'] = startDate
                save_data(data)
                await ctx.send(f'{title} has {pageCount} pages.')
        if len(parts) == 3: #Inputted author
            if len(CandidateBooks) == 0: #No book with this title
                raise Exception('No book found with this title.')
            elif len(CandidateBooks) == 1:#One book with this title
                if CandidateBooks[0]['author'] == author: #author matches
                    CandidateBooks[0]['page count'] = pageCount
                    save_data(data)
                    await ctx.send(f'{title} has {pageCount} pages.')
                elif CandidateBooks[0]['author'] == '': #author of book is missing
                    CandidateBooks[0]['author'] = author #Fill in author
                    CandidateBooks[0]['page count'] = pageCount
                    save_data(data)
                    await ctx.send(f'Setting the author of {title} as {author}. \n It has {pageCount} pages.')
                else: #author doesn't match
                    raise Exception(f'There is no book logged entitled {title} and written by {author}.')
            elif len(CandidateBooks) >1: #Mutliple books with same title
                CandidateBooksAuthors = [book for book in CandidateBooks if book['author'] == author] #Filter for books with the same author
                if len(CandidateBooksAuthors) == 0: #Title-author combo doesn't match
                    raise Exception(f'There is no book logged entitled {title} and written by {author}.')
                elif len(CandidateBooksAuthors) == 1: #Title-author combo matches one book
                    CandidateBooksAuthors[0]['page count'] = pageCount
                    save_data(data)
                    await ctx.send(f' {title} by {author} has {startDate} pages.')
                elif len(CandidateBooksAuthors) > 1: #Title-author combo matches multiple books
                    raise Exception(f'There are multiple books logged entitled {title} and written by {author}.')
    except Exception as e:
        await ctx.send(f"❌ {e}")


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

bot.run("") #Token for bot.
