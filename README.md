# Sisyphus Counter

## Description

This is a simple Discord bot designed to run a counting game in your server. This bot was initially created for the ACM @ UT Arlington Discord server. The game involves users typing numbers in sequence, and if someone makes a mistake or tries to count twice in a row, the bot will punish them with a goofy message and restart the count. The bot keeps track of the expected number and user turns, and provides a fun and interactive way to engage your server members.

## Features

- Users take turns typing numbers sequentially.
- If a user types the correct number, they get a ✅ reaction, and the count continues.
- If a user types an incorrect number, they get a ❌ reaction, and the count restarts from 1.
- If a user tries to type the same number twice in a row, they get a special punishment message and the count restarts.
- Users can include arithmetic in their numbers, for example `2+5-2*1` instead of `5`
- Users can view the leaderboard of the top 10 counters, the record count score, and the next number
- Customizable failure messages that get sent when users make mistakes.
- Admin and operator system for server management
- MongoDB integration for persistent data storage

## Commands

### User Commands
- `sis leaderboard` (aliases: `sis leader`, `sis l`) - Displays the leaderboard of top 10 players by score
- `sis next` (aliases: `sis number`, `sis num`, `sis n`) - Shows the next number in the game
- `sis commands` - Displays the help message with available commands
- `sis record` (alias: `sis r`) - Displays the current high score

### Admin Commands
- `sis set_channel` - Sets the channel for the counting game
- `sis setnum` - Sets the expected number in the game
- `sis setadmin` - Grants admin privileges to a user
- `sis removeadmin` - Removes admin privileges from a user
- `sis ban` - Removes counting privileges from a user
- `sis unban` - Restores counting privileges to a user

### Operator Commands
- `sis setoperator` - Grants operator privileges to a user
- `sis removeoperator` - Removes operator privileges from a user

## How It Works

1. The bot listens to messages in the designated game channel.
2. Users need to type the expected number in the sequence.
3. If a user types the correct number, the bot increments the expected number.
4. If a user types the wrong number or repeats their turn, the bot sends a failure message, resets the count to 1, and starts over.
5. Admins can change the game channel by using the `sis set_channel` command in any channel.
6. The bot supports arithmetic expressions (e.g., `2+5-2*1`) for number input.
7. The bot maintains a leaderboard and tracks record scores per server.

## Technical Considerations

### Concurrency and Race Conditions
- The bot uses an async lock (`state_lock`) to ensure sequential processing of messages
- This prevents race conditions where multiple messages could be processed simultaneously, which could lead to incorrect state updates
- Each command is executed fully before processing the next, maintaining data consistency

### Security Measures
- **Input Sanitization**: Strict regex validation for arithmetic expressions
- **DOS Prevention**: 
  - Timeout mechanism using signals to prevent long-running calculations
  - Limited set of allowed operators and characters
  - No support for decimals or complex mathematical functions
- **Exploit Prevention**:
  - Removal of zero-width spaces and invisible characters
  - Stripping of Discord markdown formatting
  - Handling of various Unicode space characters
  - Protection against bold text exploits

### Database Consistency
- MongoDB integration with ReadConcern("majority") to ensure data validity
- This means a majority of nodes in the MongoDB cluster must confirm the data before it's considered valid
- Helps prevent split-brain scenarios and ensures atomicity of operations
- Particularly important for maintaining accurate scores and game state

### Performance Optimizations
- Asynchronous operations throughout using `motor` for MongoDB
- Efficient state management with atomic updates
- Minimal database reads by caching guild configurations

### Error Handling
- Graceful handling of invalid expressions
- Timeout protection for long calculations
- Fallback mechanisms for user information retrieval
- Proper cleanup of signal handlers

## Setup

If you'd like to run your own version of the bot,

1. Create a `.env` file with the following variables:
   - `BOT_TOKEN`: Your Discord bot token
   - `MONGO_URI`: Your MongoDB connection string

2. Install the required dependencies:
   - discord.py
   - motor (MongoDB async driver)
   - python-dotenv
   - numexpr

3. Run the bot using `python bot.py`

**Or, invite the original Sisyphus into your server!**

Simply invite the bot by using this link:


https://discord.com/oauth2/authorize?client_id=1318377018160844861&permissions=268435456&scope=bot

and set the game channel with `sis set_channel`

Happy Counting!

## Created by Kevin Farokhrouz :bat:
Feel free to reach out if you have any questions!
