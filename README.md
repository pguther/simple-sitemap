# simple-sitemap
Python tool to convert any file of urls into a simple text site map visualizer

## Description
simple-sitemap is a tool that allows you generate a text-based visual representation of a site map.  It is possible to either supply an input file consisting of one url per line to be mapped, or to allow the script to crawl the root url and generate its own list of urls.  Output can be in a simple format that lists only the folder and file names, or a pretty format with some more formatting that also pulls the HTML page titles for any site pages and index files.  By default the generated sitemap is written to stdout, but an output file can be specified.

## Installation

#### to install without virtualenv

<code>
pip install -r requirements.txt
</code>

#### to install with virtualenv

<code>virtualenv . <br>
source bin/activate<br>
pip install -r requirements.txt
</code>

##### to quit the virtualenv
<code>deactivate</code>

##### to remove the virtualenv
<code>rm -r bin<br>
rm -r lib<br>
rm -r include<br>
rm pip-selfcheck.json
</code>

## Usage

simple_sitemap.py [-h] --base_url BASE_URL [--input INPUT] [--max MAX] [--output OUTPUT] [--pretty] [--width WIDTH]

optional arguments:<br>
*  -h, --help&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show this help message and exit<br>
*  --base_url BASE_URL&nbsp;&nbsp;The URL of a website to crawl and map<br>
*  --input INPUT&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A file containing a list of URLs to generate a sitemap from. Takes precedence over --base_url<br>
*  --max MAX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The maximum number of URLs to use in the site map, default is 500<br>
*  --output OUTPUT&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;A file to print the sitemap to, default is stdout<br>
*  --pretty&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Changes output format to pretty<br>
*  --width WIDTH&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Width of output (without page descriptions), default is 60
