import os as os
from os import path
import glob as glob
import shutil,random
import json,math
from PIL import Image # Bu kütüphane kurulmalıdır - pip install Pillow
import imageio # Bu kütüphane kurulmalıdır -pip install imageio
import pandas as pd # Bu kütüphane kurulmalıdır - pip install pandas
import numpy as np # Bu kütüphane kurulmalıdır -pip install numpy

##################################################################
#  karakterinizin katmanlarının tanımlandığı kısımdır

layersOrder = [
    { "name": 'arkaplan', "population": 100 },
    { "name": 'halk', "population": 100 },
    { "name": 'eye', "population": 100 },
    { "name": 'glasses', "population": 30 },
    { "name": 'burun', "population": 100 }, 
    { "name": 'caphair', "population": 80 },  
    { "name": 'mouth', "population": 100 },  
]
##################################################################  
#  karakterinizin resim ölçülerinin tanımlandığı kısım
formatSize = {
    "width": 100,
    "height": 100
}
##################################################################  
#  karakterinizin katmanlarının yani özelliklerinin enderlik ayarlarının yapıldığı kısım
rarity = [
    { "key":"", "val": "orginal" ,"per":1},
    { "key": "_r", "val": "rare" ,"per":0.2},
    { "key": "_sr", "val": "super rare","per":0.1 },
]
##################################################################  
#  karakterinizin sayısı
numberCharacter = 10

##################################################################  
#dosya yollarının ayarlandığı kısım
ourPath = os.getcwd()

buildDir = ourPath + "\\build\\"
metDataFile = "_metadata.json"
layersDir = ourPath + "\\layers\\"
print(ourPath)
print(buildDir)
print(layersDir)

##################################################################  
# Ana program
class NftImage():
    def __init__(self):
        self.metadata = []
        self.attributes = []
        self.hashCode = []
        self.decodedHash = []
        self.itemRarity="orginal"
        self.file_list= []
        self.layersList = []
        self.characterNameNumber=0
    def addRarity(self,_str,rarity=rarity):
        self.itemRarity = rarity[0]["val"]
        for r in rarity:
            
            if _str.find(r["key"])>0:
            
                self.itemRarity = r["val"]
            
        return self.itemRarity
    def cleanName(self,_str,rarity=rarity):
        name = _str
        
        for r in rarity:
            _str.replace(r["key"], "")
        return name
    def getElements(self,path):
        index=0
        self.file_list=[]
        for file in glob.glob(path):
            index+=1
            fileName = os.path.basename(file)
            self.file_list.append(   {"id": index,
                                "name": self.cleanName(fileName),
                                "fileName": fileName,
                                "rarity": self.addRarity(self.cleanName(fileName))
                                })
        
        return self.file_list
    def layersSetup(self,layersDir=layersDir):
        index=0
        for layer in layersOrder:
            index+=1
            folderName = layer["name"]
            self.layersList.append(   {"id": index,
                                    "name": self.cleanName(folderName),
                                    "location": layersDir + folderName+"\\",
                                    "elements": self.getElements(layersDir + folderName+"\\*"),
                                    "position": { "x": 0, "y": 0 },
                                    "size": { "width": formatSize["width"], "height": formatSize["height"] },
                                    "population": layer["population"]
                                    })
    
    
        #print(self.layersList)
        return self.layersList
    def drawLayer(self,layerList,population=numberCharacter):
        elementCharacterList =[]
        for layer in layerList:
            elementsIDs=[]
            elementChance=[]
            for element in layer["elements"]:
                for r in rarity:
                    if element["rarity"]==r["val"]:
                        elementChance.append(r["per"])
                        elementsIDs.append(element["id"])
                # if element["rarity"]=="rare":
                #     elementChance.append(0.2)
                #     elementsIDs.append(element["id"])
                # elif element["rarity"]=="super rare":
                #     elementChance.append(0.1)
                #     elementsIDs.append(element["id"])
                # else:
                #     elementChance.append(1)
                #     elementsIDs.append(element["id"])
                
            
            #print(elementsIDs,elementChance)
            results = random.choices(elementsIDs,elementChance,k=round(population*layer["population"]/100))
            elementCharacterList.append(results)
        
         
        return elementCharacterList   
    def buildSetup(self):
        if path.exists(buildDir):
           files = glob.glob(buildDir+"*")
           for f in files:
               os.remove(f)
           
        else:
            os.mkdir(buildDir)
    def removeAllfiles(self,buildDir):
        
        for files in os.listdir(buildDir):
            path = os.path.join(buildDir, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)
    def saveLayer(self,buildDir,imageList,imageName="Character_1.png",height=256,widht=256):
        if not os.path.exists(buildDir +"tempImage.png"):
            img = Image.new("RGB", (height, widht), (256, 255, 255))
            img.save(buildDir +"tempImage.png", "PNG")
        if len(imageList)!=0 :
            
                
            # Open Front Image
            frontImage = Image.open(imageList[0])
            
            # Open Background Image
            backImage = Image.open(buildDir+"tempImage.png")
            
            # # Convert image to RGBA
            # frontImage = frontImage.convert("RGBA")
            
            # # Convert image to RGBA
            # background = background.convert("RGBA")
            
            
            # Paste the frontImage at (width, height)
            backImage.paste(frontImage, (0, 0), frontImage)
            
            # Save this image
            backImage.save(buildDir+"tempImage.png", format="png")
            imageList.pop(0)
            return self.saveLayer(buildDir=buildDir,imageList=imageList)
        else:
            self.characterNameNumber+=1
            imageName="Character_"+str(self.characterNameNumber)+".png"
            shutil.copyfile(buildDir +"tempImage.png", buildDir + imageName)
            os.remove(buildDir + "tempImage.png")
            print(imageName + " image has been created")
    def mergeList(self,elementCharacterList,population=numberCharacter):
        CharacterNameList = ["Character_"+str(index) for index in range(1,population+1)]
        allSeries=[]
        for i in range(len(elementCharacterList)):
            allSeries.append(pd.Series(test[i]))
        
        dataFrame=pd.concat(allSeries, axis=1,names=CharacterNameList)
        dataFrame=dataFrame.drop_duplicates()
        #dataFrame=dataFrame.replace(np.nan, 0)
        dataFrame=dataFrame.replace(np.nan, -1)
        
        df1 = dataFrame.values.tolist()
        _metaFile=[]
        
        for x in range(0,population):
            finalList=[]
            _itemMeta=[]
            if x>len(df1)-1:
                self.createMetaFile(_metaFile)
                return finalList
            features = df1[x]
            for ftr in range(len(features)):
                layer=layerList[ftr]
                
                if features[ftr]!=-1:
                
                    #print(layer["location"],features[ftr],layer["elements"][int(features[ftr])-1])
                    finalList.append(layer["location"]+layer["elements"][int(features[ftr])-1]['fileName'])
                    _itemMeta.append(
                        {"id":len(_metaFile),
                         "Feature_id":layer["elements"][int(features[ftr])-1]['id'],
                         "Feature_name":layer["elements"][int(features[ftr])-1]['fileName'],
                         "rarity":layer["elements"][int(features[ftr])-1]['rarity'],
                         }
                    )
            #print(listem)
            _metaFile.append(_itemMeta)
            self.saveLayer(buildDir=buildDir,imageList=finalList)
        #print(_metaFile)
        self.createMetaFile(_metaFile)
        return finalList             
    def createMetaFile(self,_metaFile):
          
        with open(buildDir+'_metaFile.json', 'w', encoding='utf-8') as f:
            json.dump(_metaFile, f, ensure_ascii=False, indent=4)
            
if __name__ == "__main__":    
    nft = NftImage()
    layerList = nft.layersSetup()
    test = nft.drawLayer(layerList)
    nft.removeAllfiles(buildDir=buildDir)
    finalList = nft.mergeList(test)




