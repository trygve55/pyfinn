🏠 Fetch real estate listing from finn.no and make available as JSON response.

Requests to finn.no uses a randomized user agent. The response data is cached (with redis).

## Example usage
- [How to use the data in a Google Spreadsheet](https://medium.com/@nikolaik/samle-boligannonser-fra-finn-no-i-et-regneark-med-google-sheets-d0e4fd2ae19f) (norwegian)

## Installation

    git clone https://github.com/trygve55/pyfinn
    cd pyfinn
    python3 -m venv .
    source bin/activate
    pip3 install fake-useragent regex requests-html simplejson

## Usage
    python3 finn.py <Finn-code>

## Terms of use
From finn.no footer (norwegian):
> Innholdet er beskyttet etter åndsverksloven. Bruk av automatiserte tjenester (roboter, spidere, indeksering m.m.) samt andre fremgangsmåter for systematisk eller regelmessig bruk er ikke tillatt uten eksplisitt samtykke fra FINN.no.
