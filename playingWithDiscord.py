import discord
from discord.ext import commands
import json
import os

sampleJSON = 'C:/Users/Computer/Downloads/PythonScripts/sampleJSON.json'

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
    Format `!addBook <book name>, <author>, <page count>, <start date>, <end date>`.

    Example:

    `!addBook The Idiot, Fyodor Dostoyevsky, 345, 2025-03-04, 2025-06-12`
    """
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        if len(parts) == 0:
            raise Exception("You must provide at a title.")
        title = parts[0]
        author = parts[1] if len(parts) > 2 else ""
        pageCount = parts[2] if len(parts) > 3 else ""
        startDate = parts[3] if len(parts) > 4 else ""
        endDate = parts[4] if len(parts) > 5 else ""
        data = load_data()
        if username not in data:
            data[username] = {'books': []}
        if any(book['title'] == title and book['author'] == author for book in data[username]['books']):
            raise Exception('You have already logged this book.')
        data[username]['books'].append({
            'title': title,
            'author': author,
            'page count': pageCount,
            'start date': startDate,
            'end date': endDate
        })
        save_data(data)
        await ctx.send(f"Book '{title}' added for user {username}.")
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Get the number of books on your or someone else\'s book log.')
async def getNumberofBooks(ctx, username = ''):
    """
    Write either `!getNumberofBooks` to get the number of books in your own booklog or `!get NumberofBooks <username>` to get someone else's.
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
    Write either `!getNumberofBooks` to get the number of books you have read or `!get NumberofBooks <username>` for someone else.
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

@bot.command(help = 'Provide a date by which you finished a book.')
async def finishBook(ctx, *, args):
    """
        Format `!finishBook <title>, <endDate>, <author>`.

        Example: `!finishBook The Idiot, 2025-06-12, Fyodor Dostoyevsky`
    """
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        if len(parts) != 3:
            raise Exception('Not the correct number of arguments.')
        title = parts[0]
        endDate = parts[1]
        author = parts[2]
        data = load_data()
        candidates = [d for d in data[username]['books'] if d.get('title') == title]
        if not candidates: #What happens if there is no book under that title
            raise Exception('This book is not currently logged.')
        titled = [d for d in candidates if d.get('author') == author] 
        if not titled: #What happened if there is no titled book under that title
            book = next(d for d in data[username]['books'] if d['title'] == title)
            book['author'] = author
            book['end date'] = endDate
            msg = f"This book was not previously assigned an author. Assigning {author} and the end date {endDate}."
        else: #Assign end date normally
            book = titled[0]
            book['end date'] = endDate
            msg = f"You finished {title} on {endDate}. Congratulations!"
        save_data(data)
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Add an author to a book title you have not previously done so to.')
async def addAuthor(ctx, *, args):
    """
        Add or overwrite the author of a book. Format as `!addAuthor <title>, <author>`, as in `!addAuthor The Idiot, Fyodor Dostoyevsky`.
    """
    try:
        username = ctx.author.name
        parts = [p.strip() for p in args.split(',')]
        title = parts[0] 
        author = parts[1] 
        data = load_data()
        booksWithTitle = [d for d in data[username]['books'] if d['title'] == title]
        if not booksWithTitle:
            raise Exception('No books by this title found.')
        if len(booksWithTitle) > 1:
            raise Exception('Multiple books with this title. Cannot resolve.')
        old_author = booksWithTitle[0].get('author', '') #Saves the old author, giving an empty string if there isn't any.
        booksWithTitle[0]['author'] = author #Updates author
        save_data(data)
        if old_author:
            await ctx.send(f"Changed author of '{title}' from {old_author} to {author}.")
        else:
            await ctx.send(f"Set author of '{title}' to {author}.")
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
            messages.append(f".")
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

@bot.command(help='Remove a book from your bookLog.')
async def removeBook(ctx, *, args):
    '''Use either `!removeBook <title>` or `!removeBook <title>, <author>` to remove a book from your bookLog.
    '''
    try:
        parts = [p.strip() for p in args.split(',')]
        title = parts[0] 
        if parts[1]:
            author = parts[1]
        else:
            author = ''
        data = load_data()
        username = ctx.author.name
        books = data[username]['books']
        candidateBooks = [book for book in books if book['title'] == title]
        if len(candidateBooks) == 1: #There's only one book with the same title
            if candidateBooks[0]['author'] == author: #If the author matches
                books.remove(candidateBooks[0])
                save_data(data)
                if title != '': #If there is an author
                    await ctx.send(f"The book {title} by {author} has been removed from your booklog.")
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


@bot.command(help='Add a beginning date to a book in your booklog.')
async def addStartDate(ctx, *, args):
    ''' Use either `!addStartDate <title> <startDate> <author>` or `!addStartDate <title> <startDate>` to set a day when you started reading a book.
    '''
    try:
        parts = [p.strip() for p in args.split(',')]
        title = parts[0] 
        startDate = parts[1] 
        if len(parts) == 3:
            author = parts[2]
        else:
            author = ''
        username = ctx.author.name
        data = load_data()
        books = data[username]['books']
        candidateBooks = [book for book in books if book['title'] == title]
        if len(candidateBooks) == 1:
            if author == '':
                candidateBooks[0]['start date'] = startDate
                save_data(data)
                await ctx.send(f"You started {title} on {startDate}.")
            else:
                if candidateBooks[0]['author'] == author:
                    candidateBooks[0]['start date'] = startDate
                    save_data(data)
                    await ctx.send(f"You started {title} by {author} on {startDate}.")
                else:
                    raise Exception('There is no book in your booklog with the specified title.')
        elif len(candidateBooks) == 0:
            raise Exception('There is no book in your booklog with the specified title.')
        elif len(candidateBooks >1):
            if author == '':
                raise Exception('There are multiple books by that title. Please specify an author.')
            else:
                candidateBooksAuthors = [book for book in candidateBooks if book['author'] == author]
                if len(candidateBooksAuthors) == 0:
                    raise Exception('There is no book in your booklog with the specified title and author.')
                if len(candidateBooksAuthors) == 1:
                    candidateBooksAuthors[0]['start date'] = startDate
                    save_data(data)
                    await ctx.send(f"You started {title} by {author} on {startDate}")
                if len(candidateBooksAuthors) > 1:
                    raise Exception('There are somehow multiple books logged with the same title and author.')
    except Exception as e:
        await ctx.send(f"❌ {e}")

@bot.command(help = 'Add a page count to a book in your booklog.')
async def addPageCount(ctx, *, args):
    '''
    Add the number of pages to a book using the command `!addPageCount <title>, <page count>` or `!addPageCount <title>, <page count>, <author>`
    '''
    try:
        parts = [p.strip() for p in args.split(',')]
        title = parts[0]
        pageCount = parts[1]
        if len(parts) == 3:
            author = parts[2]
        else:
            author = ''
        username = ctx.author.name
        data = load_data()
        books = data[username]['books']
        candidateBooks = [book for book in books if book['title'] == title]
        if len(candidateBooks) == 0: #No book by this title
            raise Exception('There is no book by this title in your reading log.')
        elif len(candidateBooks) == 1: #One book with this title
            if candidateBooks[0]['author'] == '': #Book did not previously have an author
                candidateBooks[0]['author'] = author
                candidateBooks[0]['page count'] = pageCount
                save_data(data)
                if author =='': #If the above did not assign a new author
                    ctx.send(f"The book {title} has {pageCount} pages.")
                else: #If it did
                    ctx.send(f"The book {title} by {author} has {pageCount} pages.")
            elif candidateBooks[0]['author'] != '': #The book has an author
                if candidateBooks[0]['author'] != author: #The author does not match
                    raise Exception('There is no book by this title with this author in your reading log.')
                else: #The author does match
                    candidateBooks[0]['page count'] = pageCount
                    save_data(data)
                    ctx.send(f"The book {title} by {author} has {pageCount} pages.")
        else: #Multiple books with this title
            candidateBooksTitleAuthor = [book for book in candidateBooks if book['author'] == author]
            if len(candidateBooksTitleAuthor) == 1: #One book with this title and author
                candidateBooksTitleAuthor[0]['page count'] = pageCount
                save_data(data)
                ctx.send(f"The book {title} by {author} has {pageCount} pages.")
            elif len(candidateBooksTitleAuthor) == 0: #No book with this title and author
                candidateBooksNoAuthor = [book for book in candidateBooks if book['author'] == '']
                if len(candidateBooksNoAuthor) == 1: #One book with this title and no author
                    candidateBooksNoAuthor[0]['author'] = author
                    candidateBooksNoAuthor[0]['page count'] = pageCount
                    save_data(data)
                    ctx.send(f"The book {title} by {author} has {pageCount} pages.")
                elif len(candidateBooksNoAuthor) == 0: #No book with this title and no author
                    raise Exception('There are no books with this title and author in your reading log.')
                elif len(candidateBooksNoAuthor) > 1:
                    raise Exception('There are multiple books with this title and author in your reading log.')
    except Exception as e:
        await ctx.send(f"❌ {e}")

                


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

bot.run("")