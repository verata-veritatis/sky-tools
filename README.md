## Vavrespa @ Bittrex
A series of Bittrex bots to cleanse the soul.

### Donations

If you like my work and have some spare change, please donate! I take no profit for the provided bots and everything I do is all in good fun!

```
BTC: 1PXY9zSGnxBBq2CTBa23LNTwYj3XYwoB5v
LTC: LcFpXJFkvA9SqpaKWcBt2bE2F9tY2TcDZv
```

### Credits

I want to thank **Eric Somdahl** for making my life exponentially easier with his Python API wrapper which is nothing short of amazing. Most, if not all, of my bots use Bittrex scraping functions from Eric's package. Check it out: https://github.com/ericsomdahl/python-bittrex.

### Prerequisites

To use the Vavrespa Bittrex bots, you'll need to have Python 2.7 installed (3.6 versions are currently in the works). To download Python simply head over to the downloads section at Python.org, https://www.python.org/downloads/, and download and install the most recent version of Python 2.7 (as of December 8, 2017, Python 2.7.14 is the most up-to-date iteration). All functions used by the bots from external packages are embedded into the script itself, so no need to install any other Python packages. <br/><br/>
To check that you have installed Python, open up Terminal or Command Prompt and type `python`.  You should see your version of the Python language. For example, the command line will return:
```
Python 2.7.14 (r264:75708, Sep 16 2017, 07:36:50) [MSC v.1500 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for further information.
```
If you receive an error, you want to make sure that you have added Python as an environment variable, which is explained [here](https://edu.google.com/openonline/course-builder/docs/1.10/set-up-course-builder/check-for-python.html#add-to-path).

### API Settings

You'll need to have a working API and Secret key from Bittrex, with viewing **and** trading privileges. To do this, you'll first have to set up 2-Factor Authentication from the Settings menu. 

- Click on *Settings* at the top once you are logged in on Bittrex. Go to the *Two-Factor Authentication* tab and setup 2FA.
- Go to the *API Keys* tab and click *Add New Key*. From here, you'll see that a new key will be added and you'll have to confirm this change using your authenticator code. 
- **Copy your secret key and store it, because once you click away from the page, _it's gone_.**  
- Be sure to turn on *READ INFO*, *TRADE LIMIT* and *TRADE MARKET* options. *WITHDRAW* isn't needed for the time being. 

When the bot asks you for the API key and Secret key, these are the two codes you'll want to feed it.

### Instructions

These bots are python scripts. In fact, it's probably best if you keep them on your desktop. All you need to do is right click on the *.py* file and open with Terminal or Command Prompt (as long as you installed Python properly).

### Edits & Modifications

I'm an experimental physics and mathematics student, and hardly a certified "Python expert" or programming guru. If you feel something can be done better, feel free to bring up an **issue** or **pull request**, and I'll gladly take a look!
