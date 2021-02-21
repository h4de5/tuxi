<h1 align="center">TUXI</h1>
<p align="center">A CLI tool that scrapes Google search results and SERPs that provides instant and concise answers</p>

# This is an un-official python port of the original [tuxi](https://github.com/Bugswriter/tuxi/)

##

<img src="https://i.ibb.co/sCwYpZ8/general.gif" alt="Video Preview Gif" align="right" width="500px"/>

### How does this work?

The script uses `python` to scrape Google search results and SERPs.
If the query returns several results, Tuxi will choose the most
relevant result on the basis of priority.

In addition to scraping, `tuxi` also uses `BeautifulSoup` to process and return
result.

[Watch this video for more info](https://youtu.be/EtwWvMa8muU)

> Also checkout BugsWriter's YouTube channel for more scripts like this.

## Requirements

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - CLI tool for processing HTML.

## Installation

### cURL

cURL **tuxi** to your **$PATH** and give execute permissions.

```sh
$ sudo curl -sL "https://raw.githubusercontent.com/h4de5/tuxi/python-port/tuxi.py" -o /usr/local/bin/tuxi
$ sudo chmod +x /usr/local/bin/tuxi
```

> To update, just do `curl` again, no need to `chmod` anymore.
> To uninstall, simply remove `tuxi` from your **$PATH**, for example `sudo rm -f /usr/local/bin/tuxi`.

### python in virtualenv

```sh
python3 -m pip install virtualenv
python3 -m virtualenv virtualenv
source virtualenv/bin/activate
python3 -m pip install -r requirements.txt
```

### python in local

```sh
python3 -m pip install -r requirements.txt
```

## Usage

```sh
$ tuxi.py "Is Linux better than Windows?"
---
Linux has a reputation for being fast and smooth while
Windows 10 is known to become slow and slow over
time. Linux runs faster than Windows 8.1 and Windows 10
along with a modern desktop environment and qualities of the
operating system while windows are slow on older hardware.
---
```

- Quotations are optional, but should be used if you want to search with special characters (?=!|&<>%$#/\\).
- You can also write your query as a statement, e.g: `tuxi linus torvalds birthday`.
- The -r option will make the output not have formatting, which can be convenient for use in scripts.
- The -q option silences "Did you mean?" and Tuxi's greeting on calling `tuxi`.

Use `-h` to display the help message.

```sh
$ tuxi -h
Usage: tuxi [options] query

Options:
  -h                    Show this help message and exit.
  -r                    Raw search results.
                        (no pretty output, no colors)
  -q                    Only output search results.
                        (silences "Did you mean?", greeting, usage)
  -l                    Language ISO Code - e.g. en_US or de_DE.
  -a                    Return all matching result types.

Report bugs at https://github.com/Bugswriter/tuxi/issues.
```

## Features

**Easily change query language**
Line 7 in `tuxi` contains the language variable which can be changed according the user's preference.
However, tuxi will use the system default langauge if none is set.

**Gives corrections**

```sh
$ tuxi linux torvalds birthday
> Did you mean linus?
---
28 December 1969
---
```

**When you know it's actually linux torvalds** <kbd>-q option</kbd>

```sh
$ tuxi -q linux torvalds birthday
---
28 December 1969
---
```

**Raw formatting for output (no colors)** <kbd>-r option</kbd>

> Useful for e.g scripting `notify-send`.

```sh
$ tuxi -r linux torvalds birthday
> Did you mean linus?
28 December 1969
```

**Math operations**

```sh
$ tuxi "log(30)"
---
1.4771212547196624
---
```

**Translate**

```sh
$ tuxi "I love you in japanese"
---
わたしは、あなたを愛しています
---
$ tuxi "わたしは、あなたを愛しています in english"
---
I love you
---
```

**And much more (lyrics, weather, conversions...)**

## License

This project is licensed under [GPL-3.0](./LICENSE).

## Contributing

If you want to contribute, please see [CONTRIBUTING](./.github/ISSUE_TEMPLATE/CONTRIBUTING.md).
