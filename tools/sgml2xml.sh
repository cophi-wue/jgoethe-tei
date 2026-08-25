#!/bin/sh
SP_CHARSET_FIXED=1 SP_ENCODING=utf-8 osx -c catalog -xlower -xcomment -xempty -xndata -xno-nl-in-tag "$@"
