# How to run:
1. Create env.cfg file with your token (see env-example.cfg)
2. Use Dockerfile to build and run a Docker container

---

---

# eesteclctampere_ws_22
Base project for Great Northern Health Tracking Trek. EESTEC LC Tampere workshop November 2022

## Crash course to git

- `git status`
  - returns status of the repository
- `git add <filename>`
  - stages file for commit
- `git add -A`
  - stages all changed files for commit
- `git commit -m "Commit message"`
  - commit changes to head, not yet to the remote
  - if you forget message an editor will open. propably vim, don't get scared
- `git push`
  - sends changes to remote
- `git checkout -b <branchname>`
  - creates new branch and switches to it
  - without -b handle checkout just switches from one branch to another
- `git pull`
  - fetch and merge changes from remote to your local directory

- check for more: https://confluence.atlassian.com/bitbucketserver/basic-git-commands-776639767.html
- actual git documentation: https://git-scm.com/docs/git

## 0. Installing required tools and packages

### Git if you don't have already

- `sudo apt install git`

### Package installer for Python

- `sudo apt install python3-pip`

### Python Telegram Bot 

- `pip install python-telegram-bot -U --pre`
  - pre-releases https://github.com/python-telegram-bot/python-telegram-bot/wiki/introduction-to-the-API
  - If you want to use older version like 13.0 the syntax is quite different.

### Data is stored with sqlite3 database so let's install that

- `sudo apt install sqlite3`

## 0.1. Getting access to repository

- Log in or sign up to github.
- Now let's fork this repository: https://github.com/ahvena91/eesteclctampere_ws_22
- Forking means that you take a copy of source code and start independet development on it
- main branch has few minimal examples
- if you get stuck or want to check something there's a bit more advanced sources in other branches

### 1. Installing all libraries listed in requirements

- `pip install -r requirements.txt`

## 2. Talking to botfather and getting your token

- start conversation with https://t.me/botfather
- make a copy of `env-example.cfg` and rename it to `env.cfg`
- `env.cfg` is se to .gitignore so that we wont't publish our personal bot token by accident

## 3. Check echobot and conversationbot + 1_input_test

- run `python3 echobot.py` and `python3 conversationbot.py` separately
- and figure out how they work
- after this point you should at least get familiar with
  - ConversationHandler
    - https://ptb-test.readthedocs.io/en/latest/telegram.ext.conversationhandler.html
  - CommandHandler
    - https://ptb-test.readthedocs.io/en/latest/telegram.ext.commandhandler.html
  - MessageHandler
    - https://ptb-test.readthedocs.io/en/latest/telegram.ext.messagehandler.html
- In the original repository there's separate branches with more code included if you get stuck or just want to check something for reference

![Branches](images/branches1.png)

- You may also fork the repository again 
- or just copy some of the contents

## 4. Plan your own features for the bot

- Minimum requirements would be that user is able to store data and plot it 
- But of course this is your own design 
- You may check out this features.mmd https://github.com/ahvena91/eesteclctampere_ws_22/blob/main/features.mmd
  - if you want to view it locally you need to install extension for VS Code to view it.

## 5. Storing data into sqlite3 database

- First make sure you have sqlite3 installed
- This should be useful for windows users: https://www.sqlitetutorial.net/download-install-sqlite/

- Check the changes in https://github.com/ahvena91/eesteclctampere_ws_22/tree/2_database_test
- There's two new files: `initdatabase.py` and `db_handler.py`
  - first one is creating the database and second one is used for implementing methods that use the db

  ## 5.2. Testing the database

  - Database handling can be tested by running `database_test.py` program 
  - `/new` command asks user a new datapoint which is now stored in the database by calling `add_data` method from db_handler
  - you can check that the value is indeed saved by starting sqlite3
    - `sqlite3 <nameofdatabase>`
    - `.tables` lists created data tables
    - `SELECT <data> FROM <nameoftable>` lists added datapoints
      - for example: `SELECT datapoint FROM data_table` 



