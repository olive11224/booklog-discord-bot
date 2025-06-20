# booklog-discord-bot
## Introduction
This bot serves as an indexer of reading logs. Each member of the server can register a reading log for themself, set a monthly reading goal, and enter books into the log.

##List of Commands
### Basic Commands
`!register` registers a blank booklog for the user.

`!addBook <title>, (<author>), (<page count>), (<start date>), (<end date>)` adds the specified book to the user's booklog.

`!removeBook <title>, (<author>)` removes the specified book from the user's booklog.

### Reading Goal Commands
`!addReadingGoal <# of books>` sets a number of books the user wishes to read in a month.

### Informational Commands
`!getNumberofBooks (<username>)` returns the number of books <username> has read or is reading. If <username> is omitted, the user is queried.

`!getNumberCompletedBooks (<username>)` returns the number of books <username> has completed. If <username> is omitted, the user is queried.

`!getBooks (<username>)` returns detailed information on all the books <username> has read or is reading. If <username> is omitted, the user is queried.

### Update Commands (affects the user's own booklog)
`!addAuthor <title> <author>` sets an author to the book with the specified title.

`!addStartDate <title> <startDate> (<author>)` sets a starting date for the specified book.

`!addEndDate <title> <endDate> (<author>)` sets an ending date for the specified book.

`!addPageCount <title> <pageCount> (<author>)` sets a page count for the specified book.

