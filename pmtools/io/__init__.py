"""
IO functions
"""
import sys
import os
import time

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)
PROMPT_PREFIX = '> '

def yes_or_no(text):
    d = {}
    ans = do_prompt(d, text + " (Yes/No)?")
    if ans in ['Yes', 'Y', 'y']:
        return True
    else:
        return False

class ValidationError(Exception):
    """Raised for validation errors."""

def nonempty(x):
    if not x:
        raise ValidationError("Please enter some text.")
    return x

def do_prompt(d, text, key=None, default=None, validator=nonempty):
    while True:
        if default:
            prompt = PROMPT_PREFIX + '%s [%s]: ' % (text, default)
        else:
            prompt = PROMPT_PREFIX + text + ': '
        x = raw_input(prompt)
        if default and not x:
            x = default
        if x.decode('ascii', 'replace').encode('ascii', 'replace') != x:
            if TERM_ENCODING:
                x = x.decode(TERM_ENCODING)
            else:
                print '''* Note: non-ASCII characters entered 
and terminal encoding unknown -- assuming
UTF-8 or Latin-1.'''
                try:
                    x = x.decode('utf-8')
                except UnicodeDecodeError:
                    x = x.decode('latin1')
        try:
            x = validator(x)
        except ValidationError, err:
            print '* ' + str(err)
            continue
        break
    if not key is None:
        d[key] = x
    else:
        return x
