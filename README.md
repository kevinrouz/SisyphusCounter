# Sisyphus Counter

## Description

This is a simple Discord bot designed to run a counting game in your server. This bot was created specifically for the ACM @ UT Arlington Discord server. The game involves users typing numbers in sequence, and if someone makes a mistake or tries to count twice in a row, the bot will punish them with a goofy message and restart the count. The bot keeps track of the expected number and user turns, and provides a fun and interactive way to engage your server members.

## Features

- Users take turns typing numbers sequentially.
- If a user types the correct number, they get a ✅ reaction, and the count continues.
- If a user types an incorrect number, they get a ❌ reaction, and the count restarts from 1.
- If a user tries to type the same number twice in a row, they get a special punishment message and the count restarts.
- Users can include arithmetic in their numbers, for example `2+5-2*1` instead of `5`
- Users can view the leaderboard of the top 10 counters, the record count score, and the next number
- Customizable failure messages that get sent when users make mistakes.
- Admins can set the channel for the game using the `sis set_channel` command.

## How It Works

1. The bot listens to messages in the designated game channel.
2. Users need to type the expected number in the sequence.
3. If a user types the correct number, the bot increments the expected number.
4. If a user types the wrong number or repeats their turn, the bot sends a failure message, resets the count to 1, and starts over.
5. Admins can change the game channel by using the `sis set_channel` command in any channel.
