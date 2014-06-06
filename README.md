# PushBank
Send a push notification using e-mail when a change occurs in the balance of your bank account.

## How to use PushBank
**NOTICE**: At the moment PushBank supports(tested) only python 2.7. Sadly pypy is not supported yet.

1. Clone this repository: `git clone https://github.com/ssut/PushBank`
2. Install dependency packages using pip: `pip -r requirements.pip`
3. Run following command: `./pushbank.py`
4. Edit config file. (config.py)
5. Run pushbank again!

## Troubleshooting
PLEASE check below before creating an issue.

If you create an issue, please copy the output without private information.

### 1) Check your bank account is registered to "Fast inquiry service"
* KB Star Bank: [https://obank.kbstar.com/quics?page=C018920](https://obank.kbstar.com/quics?page=C018920)
* Hana bank: [https://open.hanabank.com/flex/quick/quickService.do?subMenu=1&Ctype=B&cid=OpenB_main_Left&oid=quickservice](https://open.hanabank.com/flex/quick/quickService.do?subMenu=1&Ctype=B&cid=OpenB_main_Left&oid=quickservice)

### 2) Check your SMTP settings
* Default SMTP server is GMail(smtp.gmail.com).

## Support

The developer reside in [Ozinger IRC](http://ozinger.com), [Freenode IRC](http://freenode.net) and would be glad to help you. (IRC nickname is `ssut`)

If you think you have a found a bug/have a idea/suggestion, please **open a issue** here on Github.

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