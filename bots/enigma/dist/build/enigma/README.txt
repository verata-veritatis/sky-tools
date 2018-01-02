
## Enigma Quickfire Trading Bot @ Bittrex

## Vavrespa @ Bittrex
A series of Bittrex bots to cleanse the soul.


### Donations

If you like my work and have some spare change, please donate! I take no profit for the provided bots and everything I do is all in good fun!

```
BTC: 1PXY9zSGnxBBq2CTBa23LNTwYj3XYwoB5v
LTC: LcFpXJFkvA9SqpaKWcBt2bE2F9tY2TcDZv
```


### API Settings

You'll need to have a working API and Secret key from Bittrex, with viewing **and** trading privileges. To do this, you'll first have to set up 2-Factor Authentication from the Settings menu. 

- Click on *Settings* at the top once you are logged in on Bittrex. Go to the *Two-Factor Authentication* tab and setup 2FA.
- Go to the *API Keys* tab and click *Add New Key*. From here, you'll see that a new key will be added and you'll have to confirm this change using your authenticator code. 
- **Copy your secret key and store it, because once you click away from the page, _it's gone_.**  
- Be sure to turn on *READ INFO*, *TRADE LIMIT* and *TRADE MARKET* options. *WITHDRAW* isn't needed for the time being. 


### Instructions

Once you have your API and Secret key, open *API Keys* with TextEdit or Notepad, and replace the keys within the quotes with your own keys. Save the file and exit. Start *Enigma 1.0.12* and safe trading!


### Credits

I want to thank **Eric Somdahl** for making my life exponentially easier with his Python API wrapper which is nothing short of amazing. Most, if not all, of my bots use Bittrex scraping functions from Eric's package. Check it out: https://github.com/ericsomdahl/python-bittrex.
