# PushBank
Send a push notification using smtp server when your bank balance has been changed.

The goal of PushBank is to be drop-in replacement for SMS and save on the SMS fee that BANK charges you.

## How to use PushBank
1. Clone this repository: `git clone https://github.com/ssut/PushBank`
2. Install dependency packages using pip: `pip -r requirements.pip`
3. Run following command: `./pushbank.py`
4. Edit config file. (config.py)
5. Run pushbank again!

## Troubleshooting
Please copy the output without your private info when you create an issue.

PLEASE check below before creating an issue.

### 1) You may have to register for "Fast Inquiry Service"
* KB Star Bank: [https://obank.kbstar.com/quics?page=C018920](https://obank.kbstar.com/quics?page=C018920)
* Hana bank: [https://open.hanabank.com/flex/quick/quickService.do?subMenu=1&Ctype=B&cid=OpenB_main_Left&oid=quickservice](https://open.hanabank.com/flex/quick/quickService.do?subMenu=1&Ctype=B&cid=OpenB_main_Left&oid=quickservice)

### 2) Mail settings
* Open the `config.py` and edit `EMAIL` settings.
* I recommend you to use GMail as your SMTP server.

## Support

If you think you have a found a bug/have a idea/suggestion, please **open an issue** here on Github.

## License
PushBank is **licensed** under the **MIT** license. The terms are as follows.

```text
The MIT License (MIT)

Copyright (c) 2014 SuHun Han

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```