# WhatsOn
Scanning event websites to compile a hyper-personalised list of what's on, where, and when in the area

As a first attempt, this has been done by web scraping the [Newbury Corn Exchange events pages](https://cornexchangenew.com/all-events/) and producing a CSV file according to Google's calendar import format. While this works, the CSV format is limiting (no newlines, formatting, media). I aim to switch to [iCal format](https://datatracker.ietf.org/doc/html/rfc5545) output, which would also allow the resultant calendar to be publically hosted (eg: AWS-S3) and so linked by others. This also allows for a periodic update without having to repeat an explicit import.

I used the [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/#stable) to drive a browser onto the web pages, as most events sites will block a direct request.

## Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes. See deployment
for notes on deploying the project on a live system.

### Prerequisites

Requirements for the software and other tools to build, test and push 
- Download the [latest ChromeDriver executable](https://googlechromelabs.github.io/chrome-for-testing/#stable) for your platform
- Download this repo
- Pip Install the requirements (sorry - no requirements.txt yet) 

### Sample Tests

The web-site(s) and scapers are initially hard-coded, so just:

    python main.py
