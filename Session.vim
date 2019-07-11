let SessionLoad = 1
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/development/python/stamp
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +78 README.md
badd +32 stamp/__init__.py
badd +0 tasks.py
badd +143 stamp/export.py
badd +0 locale/nb.po
badd +0 stamp/status.py
argglobal
silent! argdel *
$argadd README.md
set stal=2
edit README.md
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
wincmd _ | wincmd |
split
wincmd _ | wincmd |
split
wincmd _ | wincmd |
split
3wincmd k
wincmd w
wincmd w
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winminheight=1 winminwidth=1 winheight=1 winwidth=1
exe 'vert 1resize ' . ((&columns * 212 + 212) / 425)
exe '2resize ' . ((&lines * 23 + 30) / 61)
exe 'vert 2resize ' . ((&columns * 212 + 212) / 425)
exe '3resize ' . ((&lines * 3 + 30) / 61)
exe 'vert 3resize ' . ((&columns * 212 + 212) / 425)
exe '4resize ' . ((&lines * 26 + 30) / 61)
exe 'vert 4resize ' . ((&columns * 212 + 212) / 425)
exe '5resize ' . ((&lines * 3 + 30) / 61)
exe 'vert 5resize ' . ((&columns * 212 + 212) / 425)
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 86 - ((21 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
86
normal! 0
wincmd w
argglobal
if bufexists('stamp/__init__.py') | buffer stamp/__init__.py | else | edit stamp/__init__.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 1 - ((0 * winheight(0) + 11) / 23)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
1
normal! 0
wincmd w
argglobal
enew
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
argglobal
if bufexists('tasks.py') | buffer tasks.py | else | edit tasks.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 9 - ((8 * winheight(0) + 13) / 26)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
9
normal! 0
wincmd w
argglobal
enew
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
lcd ~/development/python/stamp
wincmd w
2wincmd w
exe 'vert 1resize ' . ((&columns * 212 + 212) / 425)
exe '2resize ' . ((&lines * 23 + 30) / 61)
exe 'vert 2resize ' . ((&columns * 212 + 212) / 425)
exe '3resize ' . ((&lines * 3 + 30) / 61)
exe 'vert 3resize ' . ((&columns * 212 + 212) / 425)
exe '4resize ' . ((&lines * 26 + 30) / 61)
exe 'vert 4resize ' . ((&columns * 212 + 212) / 425)
exe '5resize ' . ((&lines * 3 + 30) / 61)
exe 'vert 5resize ' . ((&columns * 212 + 212) / 425)
tabedit ~/development/python/stamp/stamp/status.py
set splitbelow splitright
wincmd _ | wincmd |
split
1wincmd k
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd w
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winminheight=1 winminwidth=1 winheight=1 winwidth=1
exe '1resize ' . ((&lines * 50 + 30) / 61)
exe 'vert 1resize ' . ((&columns * 210 + 212) / 425)
exe '2resize ' . ((&lines * 3 + 30) / 61)
exe 'vert 2resize ' . ((&columns * 210 + 212) / 425)
exe '3resize ' . ((&lines * 54 + 30) / 61)
exe 'vert 3resize ' . ((&columns * 214 + 212) / 425)
exe '4resize ' . ((&lines * 3 + 30) / 61)
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 253 - ((48 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
253
normal! 0
wincmd w
argglobal
enew
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
wincmd w
argglobal
if bufexists('~/development/python/stamp/stamp/export.py') | buffer ~/development/python/stamp/stamp/export.py | else | edit ~/development/python/stamp/stamp/export.py | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 184 - ((3 * winheight(0) + 27) / 54)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
184
normal! 042|
wincmd w
argglobal
enew
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
lcd ~/development/python/stamp
wincmd w
exe '1resize ' . ((&lines * 50 + 30) / 61)
exe 'vert 1resize ' . ((&columns * 210 + 212) / 425)
exe '2resize ' . ((&lines * 3 + 30) / 61)
exe 'vert 2resize ' . ((&columns * 210 + 212) / 425)
exe '3resize ' . ((&lines * 54 + 30) / 61)
exe 'vert 3resize ' . ((&columns * 214 + 212) / 425)
exe '4resize ' . ((&lines * 3 + 30) / 61)
tabedit ~/development/python/stamp/locale/nb.po
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winminheight=1 winminwidth=1 winheight=1 winwidth=1
exe 'vert 1resize ' . ((&columns * 212 + 212) / 425)
exe 'vert 2resize ' . ((&columns * 212 + 212) / 425)
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 249 - ((42 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
249
normal! 0
wincmd w
argglobal
if bufexists('~/development/python/stamp/locale/nb.po') | buffer ~/development/python/stamp/locale/nb.po | else | edit ~/development/python/stamp/locale/nb.po | endif
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let s:l = 184 - ((34 * winheight(0) + 29) / 58)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
184
normal! 07|
wincmd w
exe 'vert 1resize ' . ((&columns * 212 + 212) / 425)
exe 'vert 2resize ' . ((&columns * 212 + 212) / 425)
tabnext 1
set stal=1
if exists('s:wipebuf') && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 winminheight=1 winminwidth=1 shortmess=filnxtToOFc
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
