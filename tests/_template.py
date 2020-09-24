#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

try:
    import os
    
except Exception as e:
    print(f"Import error: {str(e)} line {sys.exc_info()[-1].tb_lineno}, check requirements.txt")
    sys.exit(1)