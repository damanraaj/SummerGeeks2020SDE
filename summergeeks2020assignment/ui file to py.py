import PyQt5.uic
def func(inFile):
        outPath=inFile[0:inFile.find(".ui")]+".py"
        out=open(outPath,'w')
        PyQt5.uic.compileUi(inFile,out)
        return True
func("UI.ui")