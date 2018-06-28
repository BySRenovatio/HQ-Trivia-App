HotKeySet("{END}", "quit")
HotKeySet("{TAB}", "pozitie")

Global $Xx = 0
Global $Yy = 0

While 1
   Sleep(1000)
WEnd

Func quit()
   Exit 0
EndFunc

Func pozitie()
	Local $aPos = MouseGetPos()
	ToolTip('X: ' & $aPos[0] - $Xx & ', Y: ' & $aPos[1] - $Yy)
EndFunc
