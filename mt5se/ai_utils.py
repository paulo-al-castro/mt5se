# This file is part of the mt5se package
#  mt5se home: https://github.com/paulo-al-castro/mt5se
# Author: Paulo Al Castro
# Date: 2020-11-17


"""

 Contém classes para transformar time series in ARFF 
Problema:
Sabendo dados de tempo=0 até t. Estimar Preco(t+h) pela técnica A, onde h é o horizonte de tempo.

A serie historica total é de 0 até N

Hipoteses simplificadoras:
Tempo Discretizado 
Preço-Real-Final discretizado por Horizonte

Para cada horizonte h define-se Max(h) e numClasses (numero impar>2, para sempre incluir N, H* e L*)

step=2*Max(h)/numClasses
Variacao=(Preco(t+h)/Preco(t)-1)

Limite==Max
indexClasse={L((numclasses-1)/2)...L3,L2,L1,N,H1,H2,H3...H((numclasses-1)/2)}
do 
	Se Variacao<Limite {
	  classe=indexClasse
	  break;
	}
	Se Limite>Max(h) {
	  classe=ultimaClasse
	  break;
	}
	else {
	   indexClasse++; 
	  Limite=Limite+step
	}
while(true);



Preco-real=
Preco-Real= truncarIntervalo[-Max(h)*10,Max(h)*10, Arredondar{(Preco(t+h)/Preco(t)-1)*1000}]
assim Preco-Real será um valor inteiro, (se Max(h)=100 ) com intervalo de variacao de +100% a -100% com 
precisão de 0.1, isto é pode-se prever




Para um dado advisor apenas alguns valores calculados a partir de um certa janela passada sao signficativos.

Digamos n valores das series S1, S2. Seja S1(t-n), ...s1(t) os ultimos dados disponiveis. Dado S1(t+1) seria o primeiro
valor futuro, isto é nao disponivel no momento...

Assim, pode-se reduzir as time series para o arff

S1(n)...s1(1);S2(n)...S2(1);Preço-Real-Final-Horizonte=Preco(t+h)

Onde t =[0,N], o periodo total 

Assim seriam geradas N-n-h instancias para o ARFF definido por um Advisor e um Horizonte


private boolean createArff(String fileName,StringBuffer tab,
			String discretization,int n) {
		try {
			PrintWriter fout = new PrintWriter (new OutputStreamWriter 
					(new FileOutputStream (fileName), "UTF-8"));
			fout.println("@relation technical_"+fileName+".symbolic");

			for (int i = 1; i <= n; i++) 
				fout.println("@attribute open"+i+" numeric");	
			
			for (int i = 1; i <= n; i++) 
				fout.println("@attribute close"+i+" numeric");
			for (int i = 1; i <= n; i++)
				fout.println("@attribute max"+i+"  numeric");
			for (int i = 1; i <= n; i++)
				fout.println("@attribute min"+i+"  numeric");
			for (int i = 1; i <= n; i++)
				fout.println("@attribute avg"+i+"  numeric");
			for (int i = 1; i <= n; i++)
				fout.println("@attribute volume"+i+"  numeric");
			
			fout.println("@attribute numericTarget numeric");
			fout.println("@attribute target {"+discretization+"}");
			fout.println("@data");
			fout.println(tab.toString());
			fout.flush();
			fout.close();
			fout=null;
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return false;
	}

"""
import numpy as np
import pandas as pd


# X is an array of arrays with values 
def ts2Dataset(X,timeFrame):
    ds=np.array()
    for line in range(len(X)-timeFrame):
        for x in X:
            for i in range(timeFrame):
                ds=ds.append(x[line+i])

    n_fields=len(X)
    size=len(ds)
    ds.reshape(size/(n_fields*timeFrame),n_fields*timeFrame)
    return ds
# From bars to dataset
def bars2Dataset(bars,target,timeFrame,horizon=1):
	ds=pd.DataFrame()
	lines=len(bars)
	for time in range(timeFrame):
		for s in bars.keys():
			aux=bars[s][time:lines-horizon-timeFrame+time]
			aux=aux.reset_index(drop=True)
			#del aux['index']
			#print('aux type=',type(aux))
			ds[s+str(time)]=aux
	#print(bars[target][timeFrame+horizon:].shift(-timeFrame),' timeF=',timeFrame,' h=',horizon  )
	aux=bars[target][timeFrame+horizon-1:]
	aux=aux.reset_index(drop=True)
	#del aux['index']
	ds['target']=aux
	return ds

def fromDs2NpArrayAllBut(ds,fieldList):
	all=ds.keys()
	for f in fieldList:
		all=all.drop(f)
	fieldList=[]
	for f in all:
		fieldList.append(f)
	return fromDs2NpArray(ds,fieldList)

	
def fromDs2NpArray(ds,fieldList=[]):
	nfields=len(fieldList)
	#print('nfields=',nfields)
	if nfields==0:
		return None
	elif nfields==1:
		return np.array(ds[fieldList[0]])
	else:
		a=np.array(ds[fieldList[0]])
	
	for i in range(1,nfields):
		a=np.column_stack((a,np.array(ds[fieldList[i]])))
	return a



def discTarget(discretizer,target):
	x=np.array(target)
	x=x.reshape(-1,1)
	dx=discretizer.fit_transform(x) 
	return dx
	
############### temp
#def bars2Dataset(bars,target,timeFrame,horizon=1):
#	ds=pd.DataFrame()
#	new_col = pd.Series([],dtype='float64') 
#	lines=len(bars)
#	for time in range(timeFrame):
#		for s in bars.keys():
#			for i in range(time,lines-horizon-timeFrame+time):
#				#ds[s+str(time)]=bars[s][time:lines-horizon-timeFrame+time].shift(-time)
#				new_col[i]=bars[s][i]
#			ds[s+str(time)]=new_col
#			new_col = pd.Series([])
#	#print(bars[target][timeFrame+horizon:].shift(-timeFrame),' timeF=',timeFrame,' h=',horizon  )
#	new_col = pd.Series([])
#	for i in range(timeFrame+horizon,lines):
#		new_col[i]=bars[target][i]
	#ds['target']=bars[target][timeFrame+horizon:].shift(-time)
#	ds['target']=new_col
#	return ds
##############
def y(y,timeFrame):
    return y[-timeFrame:]


"""
  	for (int line = 0; line < tab.getNumberOfRows()-n-numberOfDays; line++) {
		  	//uma linha 
			  //open
		  	  for (int i = 0; i < n; i++) {
				str.append(tab.get(0,line+i)+",");
			  }
		  	 //close
		  	 for (int i = 0; i < n; i++) {
					str.append(tab.get(1,line+i)+",");
				  }
		  	 //high
		  	 for (int i = 0; i < n; i++) {
					str.append(tab.get(2,line+i)+",");
				  }
		  	//low
		  	 for (int i = 0; i < n; i++) {
					str.append(tab.get(3,line+i)+",");
				  }
		  	//avg
		  	 for (int i = 0; i < n; i++) {
					str.append(tab.get(4,line+i)+",");
				  }
		    //volume
		  	 for (int i = 0; i < n; i++) {
					str.append(tab.get(5,line+i)+",");
			 }
		  	 
            """

