from anycast import Object
from collections import Counter #graphs 

class Output(object):
    def __init__(self):
        self.cdf=[]
        
    def generateRttCDFs(self,output,rtt,allrtt):
        allCDFs=[]
        allCDFs.append(self.generateCDF("Circles output of iGreedy (i.e., used for geolocation)",rtt))
        allCDFs.append(self.generateCDF("All circles",allrtt))
        self.writeDataToFile("dataCDFRtt",output,allCDFs)

    def generateTtlCDFs(self,output,ttl,allTtl):
        allCDFs=[]
        allCDFs.append(self.generateCDF("Ttl in the output of iGreedy",allTtl))
        allCDFs.append(self.generateCDF("All ttl",ttl))
        self.writeDataToFile("dataCDFTtl",output,allCDFs)

    def generateCDF(self,key,dataCDF):
        total=len(dataCDF)
        dataCDF.sort()
        count=1
        data=Object()
        data.key= key
        data.values=[]
        #data.values.append([0,0.1]) #initial point
        for d in dataCDF:
            if(float(d)>6371): #bad trick to plot the rtt cdf until the earth radius, dataset is ordered
                 return data.to_JSON()
            if(float(d)>0):
                data.values.append( [ count/float(total),int(d)])
                count+=1
        return data.to_JSON()

    def generatePlatfromPie(self,output,numberPlanetlabVp,numberRipeVp):
        dataPlatform=[]
        data=Object()
        data.label= "PlanetLab"
        data.value=numberPlanetlabVp
        dataPlatform.append(data.to_JSON())
        data.label= "Ripe"
        data.value=numberRipeVp
        dataPlatform.append(data.to_JSON())
        self.writeDataToFile("dataPlatforms",output,dataPlatform)

    def generateCountryPie(self,output,statistic):
        dataCountry=[]
        dataPie=Counter(statistic)
        #dataPie.most_common(20)
        othersValue=0
        counterCountry=0
        for key,value in dataPie.most_common():
            if(counterCountry<20 or dataPie[key]/len(dataPie)>0.03):
                counterCountry+=1
                data=Object()
                data.label= key
                data.value= value
                dataCountry.append(data.to_JSON())
            else:
                 othersValue+=dataPie[key]
        data=Object()
        data.label= "Others"
        data.value= othersValue
        dataCountry.append(data.to_JSON())
        self.writeDataToFile("dataCountry",output,dataCountry)

    def writeDataToFile(self,nameVar,output,dataToWrite):
        json=open(output,"w")
        json.write("var "+nameVar+"=[\n")
        json.write(',\n'.join(dataToWrite))
        json.write("]\n")
        json.close()