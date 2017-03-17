#!/usr/bin/env python
# Author: Anton Karazeev <anton.karazeev@gmail.com>
# Description: script to install ipy2pdf script - just
#              moves it to /usr/local/bin directory

import os

if not os.path.exists('ipy2pdf'):
    print('> Where is ipy2pdf file? o_O')
    exit()

full_path = os.path.realpath('ipy2pdf')

# os.system('ln -s {} /usr/local/bin/ipy2pdf'.format(full_path))
os.system('cp {} /usr/local/bin/ipy2pdf'.format(full_path))

print('Installed :)')
