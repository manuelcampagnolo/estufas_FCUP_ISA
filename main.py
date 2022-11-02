import qgis # already loaded
import processing # idem
import os # file management
import requests # to add xyz layer
from osgeo import ogr # connection to geopackage
import re
import rasterio
from rasterio.warp import reproject, Resampling, calculate_default_transform # reproject with rasterio
from osgeo import gdal # 
from osgeo.gdalconst import GA_Update # no data

# load auxiliary functions
folderfunctions=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\scripts_gee_py_R\scripts_python_functions'
exec(open(os.path.join(folderfunctions,'auxiliary_functions.py').encode('utf-8')).read())


parent=iface.mainWindow() # necessary for QMessageBox

# project and data set CRS
my_crs=3763
# Create project
myproject,mycanvas= my_clean_project()
# Define root (layers and groups)
myroot = myproject.layerTreeRoot()
myroot.clear() # Clear any information from this layer tree (layers and groups)
bridge = QgsLayerTreeMapCanvasBridge(myroot, mycanvas)
# set project CRS
myproject.setCrs(QgsCoordinateReferenceSystem(my_crs))

# DATA
# data structure for tif files: myfolder/'resultados'/'Tiffs'/str(year))
myfolder=r'C:\Users\mlc\OneDrive - Universidade de Lisboa\Documents\investigacao-projectos-reviews-alunos\UPorto-estufas'
myfoldertiffs=os.path.join(myfolder,'resultados','Tiffs')
years=[str(f) for f in os.listdir(myfoldertiffs) if not os.path.isfile(os.path.join(myfoldertiffs,f)) and re.search('20',f)]
mylegend={
0: ('unclassified',QColor('gray'),0), # label, color, opacity from 0 (transparent) to 1 (opaque)
1: ('estufa', QColor('red'),0.4), 
2: ('outros', QColor('green'),0.2),
6: ('artificializado', QColor('yellow'),0.2),
7: ('praias', QColor('orange'),0.2),
8: ('agua1', QColor('blue'),0.2),
9: ('agua2', QColor('blue'),0.2)}


# create dictionary for raster legend # label: (color, limite)
# determine valestufa
rlegend={}
for val, (label, Qcol, opac) in mylegend.items():
    if label=='estufa': valestufa=int(val)
    rlegend.update({label: (Qcol, int(val))})

#0 - NaN
#1 - Estufa
#2 - Não estufa
#6 - Artificial 
#7 - Praias
#8 - Água 1
#9 - Água 2

# NUTS
nuts3=my_add_vector_layer(os.path.join(myfolder,'NUTS3.gpkg'),'NUTS3')
mycanvas.setExtent(nuts3.extent())
mycanvas.refresh()

res=QMessageBox.question(parent,'Question', 'Adicionar Google satellite?' )
if res==QMessageBox.Yes:
    # add xyz layer Google Satellite
    service_url = "mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" 
    service_uri = "type=xyz&zmin=0&zmax=21&url=https://"+requests.utils.quote(service_url)
    tms_layer = iface.addRasterLayer(service_uri, "Google Satellite", "wms")

myproject.setCrs(QgsCoordinateReferenceSystem(my_crs))
mycanvas.setExtent(nuts3.extent())
mycanvas.refresh()

#
#def return_regions(myfolder,year):
#    aux=os.path.join(myfoldertiffs,str(year))
#    print(aux)
#    return [f.split('2019')[0] for f in os.listdir(aux) if os.path.isfile(os.path.join(aux,f)) and re.search('.*tif$',f)]
#
## todas as regiões
#regioes=return_regions(myfolder,2019)

# um subconjunto de regiões
regioes=['Alentejo Litoral', 'Algarve',  'Area Metropolitana de Lisboa', 'Area Metropolitana do Porto','Oeste']

# Input Dialog
myoption, ok = QInputDialog.getItem(parent, "select:", "Região", regioes, 0, False)
print(myoption)

## create group
#node_group = myroot.addGroup(myoption).setIsMutuallyExclusive(True)
#mygroup = myroot.findGroup(myoption)
#
# file paths to read for myoption (all years)

year=2020
myopacity=0.1
mylayers=[]
for year in sorted(years): 
    aux=os.path.join(myfoldertiffs,str(year))
    L=[f for f in os.listdir(aux) if os.path.isfile(os.path.join(aux,f)) and re.search(myoption+'.*tif$',f)]
    L3763=[f for f in os.listdir(aux) if os.path.isfile(os.path.join(aux,f)) and re.search(myoption+'.*3763.tif$',f)]
    if len(L3763)==1: L=L3763 # there is a file with crs 3763
    if not len(L)==1: stop # if does not stop, it will create file 3763
    # copy qml if needed
    # copy qml file if necessary
    # inputs: layer and dictionary with label: (color, limite)
    fn=os.path.join(myfoldertiffs,str(year),L[0])
    ln=myoption+'-'+str(year)
    rlayer=QgsRasterLayer(fn,ln)
    # check CRS and reproject if needed
    if rlayer.crs().authid() != 'EPSG:3763':
        fout=os.path.splitext(fn)[0]+'_3763'+os.path.splitext(fn)[1]
        dst_crs='EPSG:3763'
        reproject_rasterio(fn, fout, dst_crs)
        rlayer=QgsRasterLayer(fout,ln)
    # create legend using dictionary rlegend
    myproject.addMapLayer(rlayer)
    # change rlend for "estufa"
    myopacity+=0.1
    create_raster_ramp_legend(rlayer,rlegend, type='Exact', myopacity=myopacity)
    mylayers.append(ln)

# zoom para rlayer
mycanvas.setExtent(rlayer.extent())
mycanvas.refresh()

# combine years: each pixel has a binary code (xyz) for x=2019, y=2020, z=2021
exp='100*("'+mylayers[0]+'@1" = '+ str(valestufa)+')'
exp=exp+'+10*("'+mylayers[1]+'@1" = '+ str(valestufa)+')'
exp=exp+'+1*("'+mylayers[2]+'@1" = '+ str(valestufa)+')'
dict_params={'EXPRESSION': exp, 'LAYERS': mylayers}
rlayer=my_processing_run("qgis:rastercalculator",{},dict_params,'estufas_111')

# check nodata value
nodatavalue=rlayer.dataProvider().sourceNoDataValue(1)

# save rlayer as tif
if False: 
    fout=os.path.join(myfoldertiffs,myoption+'_111.tif')
    pipe = QgsRasterPipe()
    pipe.set(rlayer.dataProvider().clone())
    file_writer = QgsRasterFileWriter(fout)
    file_writer.writeRaster(pipe, rlayer.width(), rlayer.height(), rlayer.extent(), rlayer.crs())

# Polygonize, which takes time (or use existing file)
fout=os.path.join(myfolder,myoption+'_polys_estufas.gpkg')
if os.path.exists(fout):
    res=QMessageBox.question(parent,'Question', 'Existe ficheiro polys_estufas. Usar?' )
if res==QMessageBox.No or not os.path.exists(fout):
    # Polygonize and obtain polygons with DN=0, 1, 10, 11, 100, 101, 110, 111
    dict_params={'BAND':1,'FIELD':'DN','EIGHT_CONNECTEDNESS':True}
    mylayer=my_processing_run("gdal:polygonize",'estufas_111',dict_params,'polys_111')
    # Select polygons with value not 0
    dict_params={'EXPRESSION': ' "DN" != 0'}
    vlayer=my_processing_run("native:extractbyexpression",'polys_111',dict_params,'polys_estufas')
    # save polygons to fout
    vlayer.selectAll()
    processing.run("native:saveselectedfeatures", {'INPUT': 'polys_estufas','OUTPUT': fout})
else: 
    vlayer=my_add_vector_layer(fout,'polys_estufas')

# create legend for polygonized multiannual map of 'estufas'
mylegend111={
'..-..-21': ('001',QColor('pink'),1),
'..-20-21': ('011',QColor('orange'),1),
'19-20-21': ('111',QColor('red'),1),
'19-20-..': ('110',QColor('light blue'),1),
'19-..-..': ('100',QColor('blue'),1),
'19-..-21': ('101',QColor('yellow'),1),
'..-20-..': ('010',QColor('brown'),1)}
create_categorized_legend_3_arg(vlayer,'DN',mylegend111)
my_remove_layer('estufas_111')
