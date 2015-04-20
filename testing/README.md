## Testing

This directory contains the scripts I use to test my code.
Some people (e.g. [this post](http://www.mozillascience.org/effective-code-review-for-journals))
suggest that scientists should publish tests for all (or most) of their code,
much like a software engineer would.
I've certainly not reached that level of test coverage
(it's a nice ideal that I might one day achieve)
and have instead taken the approach of only testing code
where I do something particularly novel and/or 
the accuracy of the results isn't easily confirmable via a simple check of the output.

### How to run the test scripts from the command line

For a single test file:  
`python test_um_unittest.py`   

For all test files in the `simple_example` directory:  
`python -m unittest discover simple_example` 
