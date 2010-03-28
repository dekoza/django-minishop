"""
Convenience module for access of custom voting application settings,
which enforces default settings when the main settings module which has
been configured does not contain the appropriate settings.
"""
from django.conf import settings

# The minimum and maximum values for a vote. The default value gives you the 
# options 1, 2, 3, 4 and 5.
# You could change the MAX_SCORE to 10 if you'd like a vote from 1 to 10.
# Generally, the system works if MIN_SCORE is lower than MAX_SCORE and both are
# above 0.

try:
    MIN_SCORE = settings.MIN_SCORE
    MAX_SCORE = settings.MAX_SCORE
except AttributeError:
    MIN_SCORE = 1
    MAX_SCORE = 5

SCORES = [(str(x), x) for x in range(MIN_SCORE, MAX_SCORE+1)]
VOTE_DIRECTIONS = [('clear', 0)] + SCORES
