linkrot
=======

A script (Scrapy spider) to check a list of URLs. It requires Scrapy 1.1+

To run it periodically (e.g. every 2 hours) add something
like this to crontab::

    0 */2 * * * /usr/bin/python3 /home/ubuntu/linkrot.py /home/ubuntu/urls.txt /home/ubuntu/status.jl

To analyze the results check [Link Status](notebooks/Link Status.ipynb)
notebook.
