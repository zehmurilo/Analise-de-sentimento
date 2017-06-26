import sys
from os import startfile
import basic_sentiment_analysis
import plotGraphs
from tkinter import *

splitSentences = 0
posTagSentences = 0
dictSentences = 0
flag = False
mGui = Tk()

mGui.geometry('450x450')
mGui.title('Analise de Sentimento')
mvar1 = IntVar()
mvar2 = IntVar()
mvar3 = IntVar()
ment = StringVar()
mtext = ""

def mSentiment():
	basic_sentiment_analysis.runSentiment(splitSentences, posTagSentences, dictSentences)
	if(flag == False):
		global flag
		mlabel = Label(mGui, text ='Doumento com dados das analises gerado com sucesso', fg='red').pack()
		mbuttonTag = Button(mGui, text = 'Abrir documento com explicação das Tags', command = mOpenTag).pack()
		mbuttonDoc = Button(mGui, text = 'Abrir documento de saida', command = mOpenDoc).pack()
		mlabel2 = Label(mGui, text ='Gerar Gráficos com os resultados:', fg='red').pack()
		mlabel3 = Label(mGui, text ='Selecione até 5 documentos a terem gráficos gerados: ', fg='red').pack()
		mlabel4 = Label(mGui, text ='Exemplo de entrada: 1;5;3;8', fg='red').pack()
		mEntry = Entry(mGui, textvariable = ment).pack()
		mbuttonGraphs = Button(mGui, text = 'Gerar gráficos', command = mPassValue).pack()
		mbuttonGraphAll = Button(mGui, text = 'Gerar gráfico com dados gerais', command = mPlotGraphAll).pack()
		flag = True
	
def mPassValue():
	global ment
	mtext = ment.get()

def mPlotGraph():
	global ment
	mtext = ment.get()
	plotGraphs.someGraphs(mtext)
	#chamada para o script q gera os grafcos

def mPlotGraphAll():
	#chamada para o script q gera graficos, com todos os dados
	pass
	return

def mOpenDoc():
    startfile("C:\\Users\\emanu\\Documents\\GitHub\\Analise-de-sentimento\\output\\output.txt")

def mOpenTag():
    startfile("C:\\Users\\emanu\\Documents\\GitHub\\Analise-de-sentimento\\tags.txt")

def mSplitSentences():
	global splitSentences
	if splitSentences == 0:
		splitSentences = 1
	else:
		splitSentences = 0

def mPosTagSentences():
	global posTagSentences
	if posTagSentences == 0:
		posTagSentences = 1
	else:
		posTagSentences = 0

def mDictSentences():
	global dictSentences
	if dictSentences == 0:
		dictSentences = 1
	else:
		dictSentences = 0

mlabel = Label(mGui, text ='Selecione as opções a serem retornadas no processo de Analise de Sentimento:', fg='red').pack()
check1 = Checkbutton(mGui, text = 'Split Sentences', state = ACTIVE, variable = mvar1, command = mSplitSentences).pack()
check1 = Checkbutton(mGui, text = 'Pos Tag Sentences', state = ACTIVE, variable = mvar2, command = mPosTagSentences).pack()
check1 = Checkbutton(mGui, text = 'Dictionary Sentences', state = ACTIVE, variable = mvar3, command = mDictSentences).pack()
mbutton = Button(mGui, text = 'Realizar Analise de Sentimento', command = mSentiment).pack()



mGui.mainloop()
