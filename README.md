# Incrementing value as a service

## Usage

Get next value:

`/next/<key>?auth=<auth>`

Set next value:

`/set_next/<key>/<value>?auth=<auth>`

List all keys and values:

`/list?auth=<auth>`

## Installation

`docker-compose up -d`

(optional: set `AUTH_KEY` in `docker-compose.yml`)
