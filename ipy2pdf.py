#!/usr/bin/env python

#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# Copyright (C) 2016-17 Anton Karazeev <anton.karazeev@gmail.com>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

# Usage: ./ipy2pdf notebook.ipynb
# Output: notebook.pdf

import os
import sys
import shutil

ip_name = sys.argv[1]
name = ip_name[:len(ip_name)-5]  # with '.' at the end

tex_name = ip_name[:len(ip_name)-5]+"tex"
tmp_name = "_" + tex_name

os.system("jupyter nbconvert {} --to latex".format(ip_name))

pttrn = "\usepackage{mathpazo}"
ins = "    \usepackage[T2A]{fontenc}\n"

with open(tex_name, "r") as f_old, open(tmp_name, "w") as f_new:
    flag = 1

    for line in f_old:
        f_new.write(line)
        if flag and (pttrn in line):
            flag = 0
            f_new.write(ins)

os.remove(tex_name)
os.rename(tmp_name, tex_name)

os.system("pdflatex -interaction=nonstopmode {} > /dev/null".format(tex_name))

os.remove(name+"log")
os.remove(name+"tex")
os.remove(name+"aux")
os.remove(name+"out")
